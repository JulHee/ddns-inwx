from flask import Blueprint
from flask import abort
from flask import request
from server import utils

inwx_router = Blueprint("inwx", __name__)


@inwx_router.route("/update", methods=["GET"])
def update():
    ipv4 = request.args.get("myip", default=None, type=str)
    ipv6 = request.args.get("myipv6", default=None, type=str)
    key = request.args.get("key", default=None, type=str)

    if key is None:
        return abort(403)
    elif ipv4 is None or ipv6 is None:
        return abort(400)
    else:
        data = utils.update_record(ipv4, ipv6, key)
        if data:
            return "", 200
        else:
            return abort(500)
