"""Helper functions for api routes"""
import os
from flask import current_app


def is_access_to_dataset_denied(dataset, g):
    """Checks whether access to a certian dataset is denied
    for a given user."""
    if dataset.public:
        return False
    if (dataset.user_id != g.current_user.id) and (dataset.id not in g.session_datasets):
        return True
    return False

def is_dataset_deletion_denied(dataset_id, current_user):
    """Checks whether access to a certian dataset is denied
    for a given user."""
    return dataset_id.user_id != current_user.id


def update_processing_state(datasets, db):
    """updates processing state of all datasets in the supplied iterable"""
    for dataset in datasets:
        dataset.set_processing_state(db)


def parse_description_and_genotype(form_data):
    if ("genotype" not in form_data) or (form_data["genotype"] == "null"):
        genotype = "No genotype provided"
    else:
        genotype = form_data["genotype"]
    if ("description" not in form_data) or (form_data["description"] == "null"):
        description = "No description provided"
    else:
        description = form_data["description"]
    return description, genotype


def remove_safely(file_path):
    """Tries to remove a file and logs warning with app logger if this does not work."""
    try:
        os.remove(file_path)
    except BaseException:
        current_app.logger.warning(
            f"Tried removing {file_path}, but file does not exist!"
        )

def remove_failed_tasks(tasks, db):
    for task in tasks:
        if task.get_rq_job() is None:
            continue
        if task.get_rq_job().get_status() == "failed":
            db.session.delete(task)
    db.session.commit()

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
        binsizes |= set(bins)
    return list(binsizes)
