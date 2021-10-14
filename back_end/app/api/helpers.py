"""Helper functions for api routes"""
import os
from collections import defaultdict
from flask import current_app
from ..models import (
    Intervals,
    Dataset,
    Collection,
    Task,
    IndividualIntervalData,
    AverageIntervalData,
    BedFileMetadata,
)
import numpy as np

COMMON_REQUIRED_KEYS = ["cellCycleStage", "datasetName", "perturbation", "ValueType"]

ADD_REQUIRED_KEYS = ["assembly", "filetype"]

DATASET_META_FIELDS = {
    "assembly": "assembly",
    "cellCycleStage": "cellCycleStage",
    "perturbation": "perturbation",
    "ValueType": "valueType",
    "Method": "method",
    "SizeType": "sizeType",
    "Normalization": "normalization",
    "DerivationType": "derivationType",
    "Protein": "protein",
    "Directionality": "directionality",
}

DATASET_META_FIELDS_MODIFY = {
    "datasetName": "dataset_name",
    "cellCycleStage": "cellCycleStage",
    "perturbation": "perturbation",
    "ValueType": "valueType",
    "Method": "method",
    "Normalization": "normalization",
    "DerivationType": "derivationType",
    "Protein": "protein",
    "Directionality": "directionality",
    "public": "public",
}


def modify_dataset_requirements_fulfilled(form, filetype):
    """Checks whether all fields that are needed to modiy a dataset are fulfilled"""
    form_keys = set(form.keys())
    if any(key not in form_keys for key in COMMON_REQUIRED_KEYS):
        return False
    # check metadata
    datasetTypeMapping = current_app.config["DATASET_OPTION_MAPPING"]["DatasetType"]
    value_types = datasetTypeMapping[filetype]["ValueType"]
    if form["ValueType"] not in value_types.keys():
        return False
    # check value type members
    for key, possible_values in value_types[form["ValueType"]].items():
        # skip size type
        if key == "SizeType":
            continue
        if key not in form_keys:
            return False
        # check whether field is freetext
        if possible_values == "freetext":
            continue
        # check that value in form corresponds to possible values
        if form[key] not in possible_values:
            return False
    # check whether there is a field that is unsuitable
    for key in ADD_REQUIRED_KEYS + ["SizeType"]:
        if key in form_keys:
            return False
    return True


def post_dataset_requirements_fullfilled(form):
    """checks whether form containing information to create dataset conforms
    with the passed dataset_attribute_mapping."""
    # check common things
    form_keys = set(form.keys())
    if any(key not in form_keys for key in COMMON_REQUIRED_KEYS):
        return False
    if any(key not in form_keys for key in ADD_REQUIRED_KEYS):
        return False
    # check metadata
    datasetTypeMapping = current_app.config["DATASET_OPTION_MAPPING"]["DatasetType"]
    value_types = datasetTypeMapping[form["filetype"]]["ValueType"]
    if form["ValueType"] not in value_types.keys():
        return False
    # check value type members
    for key, possible_values in value_types[form["ValueType"]].items():
        if key not in form_keys:
            return False
        # check whether field is freetext
        if possible_values == "freetext":
            continue
        # check that value in form corresponds to possible values
        if form[key] not in possible_values:
            return False
    return True


def add_fields_to_dataset_from_form(entry, form):
    """adds dataset fields that exist in form to entry."""
    for form_key, dataset_field in DATASET_META_FIELDS.items():
        if form_key in form:
            entry.__setattr__(dataset_field, form[form_key])


def add_fields_to_dataset_from_dataset(target, source):
    """adds dataset fields that exist in source to target"""
    for dataset_field in DATASET_META_FIELDS.values():
        if source.__getattribute__(dataset_field) is not None:
            target.__setattr__(dataset_field, source.__getattribute__(dataset_field))


def add_fields_to_dataset_modify(entry, form):
    """adds dataset fields that exist in form to entry."""
    for form_key, dataset_field in DATASET_META_FIELDS_MODIFY.items():
        if form_key in form:
            if form_key == "public":
                entry.__setattr__(
                    dataset_field, "public" in form and form["public"].lower() == "true"
                )
            else:
                entry.__setattr__(dataset_field, form[form_key])


def blank_dataset(entry):
    """blanks metadata fields of dataset"""
    # common fields
    for field in COMMON_REQUIRED_KEYS:
        entry.__setattr__(field, "undefined")
    # metadata_fields
    for key in DATASET_META_FIELDS_MODIFY.keys():
        if key == "public":
            continue
        entry.__setattr__(key, "undefined")


def is_access_to_dataset_denied(dataset, g):
    """Checks whether access to a certian dataset is denied
    for a given user."""
    if dataset.public:
        return False
    if (dataset.user_id != g.current_user.id) and (
        dataset.id not in g.session_datasets
    ):
        return True
    return False


def is_access_to_collection_denied(collection, g):
    """Checks whether access to a certian dataset is denied
    for a given user."""
    if collection.public:
        return False
    if (collection.user_id != g.current_user.id) and (
        collection.id not in g.session_collections
    ):
        return True
    return False


def is_dataset_deletion_denied(dataset_id, current_user):
    """Checks whether access to a certian dataset is denied
    for a given user."""
    return dataset_id.user_id != current_user.id


def update_processing_state(entries, db):
    """updates processing state of all entries (must implement set_processing_state) in the supplied iterable"""
    for entry in entries:
        entry.set_processing_state(db)


def parse_description(form_data):
    if ("description" not in form_data) or (form_data["description"] == "null"):
        description = "No description provided"
    else:
        description = form_data["description"]
    return description


def delete_collection(collection, db):
    """deletes collection and associated data."""
    assoc_data = collection.associationData.all()
    embed_data = collection.embeddingData.all()
    deletion_queue = assoc_data + embed_data
    for entry in deletion_queue:
        # remove files
        remove_safely(entry.file_path)
        if hasattr(entry, "file_path_feature_values"):
            remove_safely(entry.file_path_feature_values)
    db.session.delete(collection)


def delete_associated_data_of_dataset(dataset):
    """deletes associated data of database entries. Actual deletion of entries
    is handeled by database cascades"""
    intervals = []
    averageIntervalData = []
    individualIntervalData = []
    metadata = []
    # cooler only needs deletion of derived averageIntervalData
    if dataset.filetype == "cooler":
        averageIntervalData = AverageIntervalData.query.filter(
            AverageIntervalData.dataset_id == dataset.id
        ).all()
    # bedfile needs deletion of intervals and averageIntervalData
    if dataset.filetype == "bedfile":
        intervals = Intervals.query.filter(Intervals.dataset_id == dataset.id).all()
        averageIntervalData = AverageIntervalData.query.filter(
            AverageIntervalData.intervals_id.in_([entry.id for entry in intervals])
        ).all()
        individualIntervalData = IndividualIntervalData.query.filter(
            IndividualIntervalData.intervals_id.in_([entry.id for entry in intervals])
        ).all()
        metadata = BedFileMetadata.query.filter(
            BedFileMetadata.dataset_id == dataset.id
        ).all()
    if dataset.filetype == "bigwig":
        averageIntervalData = AverageIntervalData.query.filter(
            AverageIntervalData.dataset_id == dataset.id
        ).all()
        individualIntervalData = IndividualIntervalData.query.filter(
            IndividualIntervalData.dataset_id == dataset.id
        ).all()
    # delete files and remove from database
    deletion_queue = (
        [dataset] + intervals + averageIntervalData + individualIntervalData + metadata
    )
    for entry in deletion_queue:
        if isinstance(entry, IndividualIntervalData):
            remove_safely(entry.file_path_small)
        if hasattr(entry, "file_path") and (entry.file_path is not None):
            remove_safely(entry.file_path)
        if hasattr(entry, "file_path_sub_sample_index") and (
            entry.file_path_sub_sample_index is not None
        ):
            remove_safely(entry.file_path_sub_sample_index)


def remove_safely(file_path):
    """Tries to remove a file and logs warning with app logger if this does not work."""
    try:
        os.remove(file_path)
    except BaseException:
        current_app.logger.warning(
            f"Tried removing {file_path}, but file does not exist!"
        )


def remove_tasks(tasks, db):
    for task in tasks:
        db.session.delete(task)
    db.session.commit()


def filter_failed_tasks(tasks):
    """filters tasks for failed tasks"""
    output = []
    for task in tasks:
        if task.get_rq_job() is None:
            output.append(task)
            continue
        if task.get_rq_job().get_status() == "failed":
            output.append(task)
    return output


def remove_failed_tasks_dataset(db, dataset, region):
    """Removes all failed tasks that are associated with a particular dataset/region combination"""
    associated_tasks = (
        Task.query.join(Intervals)
        .join(Dataset)
        .filter(
            (Dataset.id == region.id)
            & (Task.dataset_id == dataset.id)
            & (Task.complete == False)
        )
        .all()
    )
    failed_tasks = filter_failed_tasks(associated_tasks)
    remove_tasks(failed_tasks, db)


def remove_failed_tasks_collection(db, collection, region):
    """Removes all failed tasks that are associated with a particular collection/region combination"""
    associated_tasks = (
        Task.query.join(Intervals)
        .join(Dataset)
        .filter(
            (Dataset.id == region.id)
            & (Task.collection_id == collection.id)
            & (Task.complete == False)
        )
        .all()
    )
    failed_tasks = filter_failed_tasks(associated_tasks)
    remove_tasks(failed_tasks, db)


def get_all_interval_ids(region_datasets):
    """Returns ids of all intervals associated with list or region datasets."""
    interval_ids = []
    for region_dataset in region_datasets:
        interval_ids.extend([entry.id for entry in region_dataset.intervals.all()])
    return interval_ids


def parse_binsizes(map):
    """returns needed binsizes from preprocessing map."""
    binsizes = set()
    for windowsize, bins in map.items():
        if windowsize != "variable":
            binsizes |= set(bins)
    return list(binsizes)


def add_average_data_to_preprocessed_dataset_map(
    average_interval_datasets, output_object, request_context
):
    for average in average_interval_datasets:
        dataset = Dataset.query.get(average.dataset_id)
        # check whether dataset is owned
        if is_access_to_dataset_denied(dataset, request_context):
            continue
        # check whether there are any uncompleted tasks for the region dataset associated with these features
        interval = Intervals.query.get(average.intervals_id)
        region_dataset = interval.source_dataset
        # check whether region_dataset is interval
        if region_dataset.sizeType == "Interval":
            windowsize = "variable"
        else:
            windowsize = interval.windowsize
        # check whether dataset is in failed or processing datasets
        if (dataset in region_dataset.processing_features) or (
            dataset in region_dataset.failed_features
        ):
            continue
        if average.value_type in ["Obs/Exp", "ICCF"]:
            output_object["pileup"][dataset.id]["name"] = dataset.dataset_name
            output_object["pileup"][dataset.id]["data_ids"][windowsize][
                average.binsize
            ][average.value_type] = str(average.id)
        else:
            output_object["lineprofile"][dataset.id]["name"] = dataset.dataset_name
            output_object["lineprofile"][dataset.id]["data_ids"][windowsize][
                average.binsize
            ] = str(average.id)


def add_individual_data_to_preprocessed_dataset_map(
    individual_interval_datasets, output_object, request_context
):
    for individual in individual_interval_datasets:
        dataset = Dataset.query.get(individual.dataset_id)
        # check whether dataset is owned
        if is_access_to_dataset_denied(dataset, request_context):
            continue
        # check whether there are any uncompleted tasks for the feature dataset
        interval = Intervals.query.get(individual.intervals_id)
        region_dataset = interval.source_dataset
        # check whether region_dataset is interval
        if region_dataset.sizeType == "Interval":
            windowsize = "variable"
        else:
            windowsize = interval.windowsize
        # check whether dataset is in failed or processing datasets
        if (dataset in region_dataset.processing_features) or (
            dataset in region_dataset.failed_features
        ):
            continue
        output_object["stackup"][dataset.id]["name"] = dataset.dataset_name
        output_object["stackup"][dataset.id]["data_ids"][windowsize][
            individual.binsize
        ] = str(individual.id)


def add_association_data_to_preprocessed_dataset_map(
    association_interval_datasets, output_object, request_context
):
    for assoc in association_interval_datasets:
        collection = Collection.query.get(assoc.collection_id)
        # check whether collection is owned
        if is_access_to_collection_denied(collection, request_context):
            continue
        # check whether there are any uncompleted tasks for the feature dataset
        interval = Intervals.query.get(assoc.intervals_id)
        region_dataset = interval.source_dataset
        # check whether region_dataset is interval
        if region_dataset.sizeType == "Interval":
            windowsize = "variable"
        else:
            windowsize = interval.windowsize
        if (collection in region_dataset.processing_collections) or (
            collection in region_dataset.failed_collections
        ):
            continue
        output_object["lola"][collection.id]["name"] = collection.name
        output_object["lola"][collection.id][
            "collection_dataset_names"
        ] = collection.to_json()["dataset_names"]
        output_object["lola"][collection.id]["data_ids"][windowsize][
            assoc.binsize
        ] = str(assoc.id)


def add_embedding_data_to_preprocessed_dataset_map(
    embedding_interval_datasets, output_object, request_context
):
    for embed in embedding_interval_datasets:
        collection = Collection.query.get(embed.collection_id)
        # check whether collection is owned
        if is_access_to_collection_denied(collection, request_context):
            continue
        # check whether there are any uncompleted tasks for the feature dataset
        interval = Intervals.query.get(embed.intervals_id)
        region_dataset = interval.source_dataset
        # check whether region_dataset is interval
        if region_dataset.sizeType == "Interval":
            windowsize = "variable"
        else:
            windowsize = interval.windowsize
        if (collection in region_dataset.processing_collections) or (
            collection in region_dataset.failed_collections
        ):
            continue
        if embed.value_type == "1d-embedding":
            output_object["embedding1d"][collection.id]["name"] = collection.name
            output_object["embedding1d"][collection.id][
                "collection_dataset_names"
            ] = collection.to_json()["dataset_names"]
            output_object["embedding1d"][collection.id]["data_ids"][windowsize][
                embed.binsize
            ] = str(embed.id)
        else:
            output_object["embedding2d"][collection.id]["name"] = collection.name
            output_object["embedding2d"][collection.id][
                "collection_dataset_names"
            ] = collection.to_json()["dataset_names"]
            output_object["embedding2d"][collection.id]["data_ids"][windowsize][
                embed.binsize
            ][embed.normalization] = str(embed.id)


def recDict():
    """Recursive defaultdict that allows deep
    assignment. recDict[0][1][2] will
    create all intermediate dictionaries."""
    return defaultdict(recDict)


def get_optimal_binsize(regions, target_bin_number):
    """given a dataframe of regions defined via (chrom, start, end) and a
    target bin number, decide which binsize to use for variable size pileup/enrichment analysis"""
    MAX_CHUNK_NUMBER = 250
    sizes = regions["end"] - regions["start"]
    max_size = np.percentile(sizes, 80)
    median_size = np.median(sizes)
    binsizes = sorted(
        [
            int(entry)
            for entry in parse_binsizes(current_app.config["PREPROCESSING_MAP"])
        ]
    )
    chunk_number = [max_size / binsize for binsize in binsizes]
    # check if first chunk_number is below 1 -> should indicate error
    if chunk_number[0] <= 1:
        return None
    # flag binsizes that are below max chunk_number
    good_binsizes = [
        (binsize, median_size / binsize)
        for index, binsize in enumerate(binsizes)
        if chunk_number[index] < MAX_CHUNK_NUMBER
    ]
    # check if any retained
    if len(good_binsizes) == 0:
        return None
    # check which binsize is closest to the target binnumber for the mean size
    best_binsize = min(good_binsizes, key=lambda x: abs(x[1] - target_bin_number))
    # return smallest one that is ok
    return best_binsize[0]


def flatten_and_clean_array(array):
    """takes numpy array and converts it to a list where
    numpy.na and +\- np.inf is convert to python None"""
    return [
        entry if not (np.isnan(entry) or np.isinf(entry)) else None
        for entry in array.flatten()
    ]