from crawler.parse_page import crawler_get
from django.core.management.base import NoArgsCommand
from apps.robots.models import  RobotsTries, Robots
from crawler.robot_start import sites_crawler

import datetime
from django.utils import timezone


def add_robot_if_not_exist(robot_name):

    try:

        robot = Robots.objects.get(name=robot_name)

    except Robots.DoesNotExist:

        print "Couldn't find record for {} adding one".format(robot_name)
        robot= Robots(name=robot_name,
                      delay=20,
                      last_start = timezone.now() - datetime.timedelta(days=7),
                      state='{}',
                      description=' ',
        rstatus = 0)
        robot.save()



class Command(NoArgsCommand):
    def handle_noargs(self, **options):


        robot_list = sites_crawler.keys()

        robot_list += ['kinopoisk_set_poster','kinopoisk_get_id']


        for robot in robot_list:

            add_robot_if_not_exist(robot)