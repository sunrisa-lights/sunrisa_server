from flask import request
from flask import jsonify

from typing import List

from app.models.shelf_grow import ShelfGrow
from app.models.grow_phase import GrowPhase

from app.job_scheduler.schedule_jobs import (
    client_get_jobs,
    schedule_grow_for_shelf,
)


def init_endpoint_listeners(app_config, app):
    @app.route("/add-job", methods=["POST"])
    def index():
        params = request.get_json()
        shelf_grows: List[ShelfGrow] = []
        for shelf_grow_json in params["shelf_grows"]:
            shelf_grow: ShelfGrow = ShelfGrow.from_json(shelf_grow_json)
            shelf_grows.append(shelf_grow)

        grow_phase: GrowPhase = GrowPhase.from_json(params["grow_phase"])
        power_level: int = params["power_level"]
        red_level: int = params["red_level"]
        blue_level: int = params["blue_level"]
        schedule_grow_for_shelf(
            app_config,
            shelf_grows,
            grow_phase,
            power_level,
            red_level,
            blue_level,
        )

        return jsonify({"success": True})

    @app.route("/get-jobs", methods=["GET"])
    def get_jobs():
        jobs = client_get_jobs()
        job_ids = []
        for job in jobs:
            job_ids.append(job.id)

        return jsonify({"job_ids": job_ids})
