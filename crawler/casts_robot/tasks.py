# coding: utf-8
from crawler.casts_robot import parse_sportbox_ru, parse_translation_live_russia_tv, parse_khl, parse_translation_championat_com, parse_ntv_plus_translation
from crawler.casts_robot.cast_utils import save_cast_dict
from videobase.celery import app
from utils.common import traceback_own


def generic_task(parse_function, service_name):
    parsed = parse_function()

    print u'Got {} casts descriptions from {}'.format(len(parsed), service_name)

    for cast_dict in parsed:

        try:
            print u"Trying to save {} cast".format(cast_dict['title'])
            save_cast_dict(service_name, cast_dict)

        except Exception, e:
            traceback_own(e)

@app.task(name='cast_sportbox_robot', queue='cast_sportbox_robot')
def sportbox_update():
    generic_task(parse_sportbox_ru, 'sportbox_ru')
    
@app.task(name='cast_liverussia_robot', queue='cast_liverussia_robot')
def liverussia_update():
    generic_task(parse_translation_live_russia_tv, 'liverussia_ru')

@app.task(name='cast_championat_robot', queue='cast_championat_robot')
def championat_update():
    generic_task(parse_translation_championat_com, 'championat_com')

@app.task(name='cast_khl_robot', queue='cast_khl_robot')
def khl_update():
    generic_task(parse_khl, 'khl_ru')

@app.task(name='cast_ntv_plus_robot', queue='cast_ntv_plus_robot')
def ntv_plus_update():
    generic_task(parse_ntv_plus_translation, 'ntv_plus')

