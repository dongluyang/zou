from zou.app import config
from zou.app.utils import emails

from zou.app.services import (
    entities_service,
    names_service,
    persons_service,
    projects_service,
    tasks_service
)
from zou.app.stores import queue_store


def send_notification(person_id, subject, message):
    """
    Send email notification to given person. Use the job queue if it is
    activated.
    """
    person = persons_service.get_person_raw(person_id)
    if person.notifications_enabled:
        if config.ENABLE_JOB_QUEUE:
            queue_store.job_queue.enqueue(
                emails.send_email,
                args=(subject, message, person.email)
            )
        else:
            emails.send_email(subject, message, person.email)
    return True


def send_comment_notification(person_id, author_id, comment, task):
    """
    Send a notification emali telling that a new comment was posted to person
    matching given person id.
    """
    person = persons_service.get_person_raw(person_id)
    if person.notifications_enabled:
        task_status = tasks_service.get_task_status(task["task_status_id"])
        (author, task_name, task_url) = get_task_descriptors(author_id, task)
        subject = "[Kitsu] %s - %s commented on %s" % (
            task_status["short_name"],
            author["first_name"],
            task_name
        )
        message = """%s wrote a comment on %s and changed the status to %s:

"%s"

To reply connect to this URL:
%s
%s
""" % (
            author["full_name"],
            task_name,
            task_status["short_name"],
            comment["text"],
            task_url,
            get_signature()
        )
        return send_notification(person_id, subject, message)
    else:
        return True


def send_mention_notification(person_id, author_id, comment, task):
    """
    Send a notification email telling that somenone mentioned the
    person matching given person id.
    """
    person = persons_service.get_person_raw(person_id)
    if person.notifications_enabled:
        (author, task_name, task_url) = get_task_descriptors(author_id, task)
        subject = "[Kitsu] %s mentioned you on %s" % (
            author["first_name"],
            task_name
        )
        message = """%s mentioned you in a comment on %s:

"%s"

To reply connect to this URL:
%s
%s
""" % (
            author["full_name"],
            task_name,
            comment["text"],
            task_url,
            get_signature()
        )
        return send_notification(person_id, subject, message)
    else:
        return True


def send_assignation_notification(person_id, author_id, task):
    """
    Send a notification email telling that somenone assigned to a task the
    person matching given person id.
    """
    person = persons_service.get_person_raw(person_id)
    if person.notifications_enabled:
        (author, task_name, task_url) = get_task_descriptors(author_id, task)
        subject = "[Kitsu] You were assigned to %s" % task_name
        message = """ %s assigned you to %s.

    To see the task details connect to this URL:
    %s
    %s
    """ % (
            author["full_name"],
            task_name,
            task_url,
            get_signature()
        )
        return send_notification(person_id, subject, message)
    return True


def get_signature():
    """
    Build signature for Zou emails.
    """
    organisation = persons_service.get_organisation()
    return """
Best,

%s Team""" % organisation["name"]


def get_task_descriptors(person_id, task):
    """
    Build task information needed to write notification emails: author object,
    full task name and task URL.
    """
    author = persons_service.get_person(person_id)
    project = projects_service.get_project(task["project_id"])
    task_type = tasks_service.get_task_type(task["task_type_id"])
    entity = entities_service.get_entity(task["entity_id"])
    (entity_name, episode_id) = names_service.get_full_entity_name(entity["id"])

    episode_segment = ""
    entity_type = "assets"
    if task_type["for_shots"]:
        entity_type = "shots"
    if project["production_type"] == "tvshow":
        episode_segment = "/episodes/%s" % episode_id

    task_name = "%s / %s / %s" % (
        project["name"],
        entity_name,
        task_type["name"]
    )
    task_url = "%s://%s/productions/%s%s/%s/tasks/%s" % (
        config.DOMAIN_PROTOCOL,
        config.DOMAIN_NAME,
        task["project_id"],
        episode_segment,
        entity_type,
        task["id"]
    )
    return (author, task_name, task_url)