import datetime

from flask import render_template, jsonify

from app.main import bp
from app.models import PredictionRecord, User
from app import db


@bp.route('/')
def dashboard():
    users = User.query.count()
    predictions = PredictionRecord.query.count()
    average_confidence = PredictionRecord.query.with_entities(db.func.avg(PredictionRecord.confidence)).scalar()
    all_confidence = PredictionRecord.query.with_entities(PredictionRecord.confidence).all()
    average_confidence = round(average_confidence, 2)
    all_confidence = [confidence[0] for confidence in all_confidence]
    standard_deviation = round((sum([(confidence - average_confidence) ** 2 for confidence in all_confidence]) / (len(
        all_confidence) - 1)) ** 0.5, 2)

    predicitons_with_feedback = PredictionRecord.query.filter(PredictionRecord.isAccurate != None).count()

    correct_predictions = PredictionRecord.query.filter_by(isAccurate=True).count()
    correct_predictions_percentage = round(correct_predictions / predicitons_with_feedback * 100, 2)

    return render_template("dashboard.html", title="Dashboard", users=users, predictions=predictions,
                           average_confidence=average_confidence, standard_deviation=standard_deviation,
                           correct_predictions_percentage=correct_predictions_percentage)


@bp.route("/dashboard/statistics_per_day", methods=["GET"])
def statistics_per_day():
    records = PredictionRecord.query.with_entities(
        db.func.date(PredictionRecord.datetime),
        db.func.count(PredictionRecord.datetime)).group_by(
        db.func.date(PredictionRecord.datetime)).all()

    results_array = []
    for record in records:
        results = {"datetime": record[0], "count": record[1]}
        results_array.append(results)

    return jsonify(results_array)


@bp.route("/dashboard/users_per_day", methods=["GET"])
def users_per_day():
    records = User.query.with_entities(
        db.func.date(User.created_at),
        db.func.count(User.created_at)).group_by(
        db.func.date(User.created_at)).where(
        User.created_at >= f'{datetime.datetime.utcnow() - datetime.timedelta(days=7)}').all()

    results_array = []
    for record in records:
        results = {"datetime": record[0], "count": record[1]}
        results_array.append(results)

    return jsonify(results_array)


@bp.route("/dashboard/predictions_per_type", methods=["GET"])
def predictions_per_type():
    records = PredictionRecord.query.with_entities(
        PredictionRecord.prediction_type,
        db.func.count(PredictionRecord.prediction_type)).group_by(
        PredictionRecord.prediction_type).all()

    results_array = []
    for record in records:
        results = {"type": record[0].name, "count": record[1]}
        results_array.append(results)

    return jsonify(results_array)


@bp.route("/dashboard/percentage_accurate_predictions/<prediction_type>", methods=["GET"])
def percentage_accurate_predictions(prediction_type):
    predicitons_with_feedback = PredictionRecord.query.filter(PredictionRecord.isAccurate != None, PredictionRecord.prediction_type == prediction_type).count()
    correct_predictions = PredictionRecord.query.filter_by(isAccurate=True, prediction_type=prediction_type).count()
    try:
        correct_predictions_percentage = round(correct_predictions / predicitons_with_feedback * 100, 2)
    except ZeroDivisionError:
        correct_predictions_percentage = "No hay datos suficientes"

    return jsonify(correct_predictions_percentage)



