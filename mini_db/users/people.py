import pickle
import os
from datetime import datetime
from flask import g, jsonify, Blueprint
from flask import make_response, abort, redirect, url_for, render_template
from commp.src.logger import LOG
from commp.src.db_operater import insert_people_one, get_timestamp
from __path__ import project_path, data_path
logger = LOG.ret_logger(__name__)

api = Blueprint('api', __name__, url_prefix='/api')

PEOPLE = {
    "Jack": {
        "lname": "Jack",
        "fname": '1:ab12',
        'price': '10',
        "timestamp": get_timestamp()
    }
}

# Data to server with our API
def pick_dump(file_name, PEOPLE):
    with open(file_name, 'wb') as f:
        pickle.dump(PEOPLE, f, pickle.HIGHEST_PROTOCOL)
        logger.info(f"picker write info:{PEOPLE}")
        return True

def ret_file_name(file_path, n=0):
    """按规则产生数据文件名，并写入示例"""
    time_stuff = f"{datetime.now().year}-{datetime.now().month}-{datetime.now().day}-{n}"
    _file_name = f"{file_path}/data.pickle.{time_stuff}"

    # 每日创建data文件并写入示例
    if not os.path.exists(_file_name):
        pick_dump(_file_name, PEOPLE)
    return _file_name

def ret_last_file():
    """return the last file which one best new"""
    if not os.listdir(data_path):
        file_name = ret_file_name(data_path, n=0)
    logger.debug(f"os.path:{data_path} last file:{os.listdir(data_path)}")
    return os.path.join(data_path, os.listdir(data_path)[-1])


# 数据文件全局变量 file name
file_name = ret_last_file()

def pick_read(read_name):
    """read data file
    :read_name: the pickle data file name
    :return: the contact in data file name"""
    try:
        with open(read_name, 'rb') as om:
            PEOPLE = pickle.load(om)
            return PEOPLE
    except FileNotFoundError as fe:
        logger.error(f"picker read file {read_name} fail error info:{fe}")
        file_name = ret_last_file()
        PEOPLE = pick_read(file_name)
        logger.info(f"picker read info:{PEOPLE}")
        return PEOPLE

@api.route('/<lname>/<fname>/<price>', methods=['GET', 'POST'])
def create(lname, fname, price):
    """
    This func create a new person in the people structure based on the passed in person data
    :param person: person to create in people structure
    :return:  201 on succes, 406 on person exists
    """
    person = {'lname':lname, 'fname':fname, 'price':price}
    lname = person.get("lname", "Jack")
    fname = person.get("fname", 'RiceMeat')
    price = person.get("price", 0)

    # 从远程服务器返回price

    PEOPLE = {}
    # Does the person exist already?
    if lname not in PEOPLE and lname is not None:
        PEOPLE[lname] = {
            'lname': lname,
            'fname': fname,
            'price': price,
            'timestamp': get_timestamp(),
        }
        logger.info(f"on datafile:{file_name} create bill with name:{lname} all food bill:{PEOPLE}")
        # pick_dump(file_name, PEOPLE)
        if insert_people_one(username=lname, fname=fname, price=price):
            return render_template('auth/login.html')
        else:
            return PEOPLE[lname], 201

    # Otherwise, it exist, here will raise error
    else:
        abort(406, "At data file:{file} Person with name {lname} already exists".format(file=file_name, lname=lname))


def total():
    """"""
    return "total"

def create_auth_app():
    app = ...


