# coding: utf-8
from email.mime.text import MIMEText
import json
import smtplib
from celery import Task
import datetime
from django.forms.models import model_to_dict
import djcelery
from djcelery.models import TaskMeta
from djcelery.picklefield import decode
from djcelery.views import task_status
from apps.robots.models.robots_logs import RobotsInfoLogging
from apps.robots.models.robots_mail_list import RobotsMailList
from apps.users.tasks import send_template_mail, send_statistic_to_mail

__author__ = 'vladimir'


def write_logs_to_console():
    for task in TaskMeta.objects.all():
        result = task_status(None, task.task_id)
        print "decoded", decode(task.meta)
        js = json.loads(result.content)
        task_result = js['task']['result']
        if task_result is not None:
            print result


def create_structures_string(robot_name, location_ids):
    return "Robot {} returned {} locations: {} ".format(str(robot_name), len(location_ids), location_ids)


def write_logs_to_table(robot_name, location_ids):
    RobotsInfoLogging.objects.create(robot_name=robot_name, locations=location_ids, log_time=datetime.date.today())


class DebugTask(Task):
    abstract = True

    def after_return(self, *args, **kwargs):
        try:
            print create_structures_string(args[1][0], args[1][1])
            write_logs_to_table(args[1][0], args[1][1])
        except Exception, e:
            pass


def collect_logs(date=datetime.datetime.now().date()):
    robo_dict={}
    for robolog in RobotsInfoLogging.objects.all():
        if robolog.log_time.date() == date:
            if robolog.robot_name in robo_dict:
                robo_dict[robolog.robot_name] += ", " + robolog.locations
            else:
                robo_dict[robolog.robot_name] = robolog.locations

    return robo_dict


def create_one_email_report_str_for_statistic(robo_name, location_ids):
    result = "<p> <span>Robot </span> <span>{0}</span> <span> returned {1}</span> <span> locations: {2}</span> </p>".format(robo_name, len(location_ids.split()), location_ids)
    return result


def send_statistic_to_email_for_each_robot():
    str_for_send = ""
    robo_dict = collect_logs()
    for key, value in robo_dict.iteritems():
        one_report_str = create_one_email_report_str_for_statistic(key, value)
        str_for_send += one_report_str
    to = []
    for item in RobotsMailList.objects.all():
        to.append(item.email)
    if len(to) == 0:
        return
    subject = "robots logs"
    kwrg = {
            'subject': subject,
            'text': str_for_send,
            'to': to,
           }
    send_statistic_to_mail.apply_async(kwargs=kwrg)