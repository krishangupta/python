import json
import os
from lettuce import step, world
from bigml.model import Model
from bigml.cluster import Cluster
from bigml.multimodel import MultiModel
from bigml.multivote import MultiVote

@step(r'I retrieve a list of remote models tagged with "(.*)"')
def i_retrieve_a_list_of_remote_models(step, tag):
    world.list_of_models = [world.api.get_model(model['resource']) for model in
                            world.api.list_models(query_string="tags__in=%s" % tag)['objects']]


@step(r'I create a local model')
def i_create_a_local_model(step):
    world.local_model = Model(world.model)


@step(r'I create a local prediction for "(.*)"')
def i_create_a_local_prediction(step, data=None):
    if data is None:
        data = "{}"
    data = json.loads(data)
    world.local_prediction = world.local_model.predict(data)


@step(r'I create a local cluster')
def i_create_a_local_cluster(step):
    world.local_cluster = Cluster(world.cluster)


@step(r'I create a local centroid for "(.*)"')
def i_create_a_local_centroid(step, data=None):
    if data is None:
        data = "{}"
    data = json.loads(data)
    for key, value in data.items():
        if value == "":
            del data[key]
    world.local_centroid = world.local_cluster.centroid(data)


@step(r'the local centroid is "(.*)" with distance "(.*)"')
def the_local_centroid_is(step, centroid, distance):
    if str(world.local_centroid['centroid_name']) == centroid:
        assert True
    else:
        assert False, "Found: %s, expected: %s" % (str(world.local_centroid['centroid_name']), centroid)
    if str(world.local_centroid['distance']) == distance:
        assert True
    else:
        assert False, "Found: %s, expected: %s" % (str(world.local_centroid['distance']), distance)


@step(r'I create a proportional missing strategy local prediction for "(.*)"')
def i_create_a_proportional_local_prediction(step, data=None):
    if data is None:
        data = "{}"
    data = json.loads(data)
    world.local_prediction = world.local_model.predict(
        data, with_confidence=True, missing_strategy=1)


@step(r'I create a prediction from a multi model for "(.*)"')
def i_create_a_prediction_from_a_multi_model(step, data=None):
    if data is None:
        data = "{}"
    data = json.loads(data)
    world.local_prediction = world.local_model.predict(data)


@step(r'the local prediction is "(.*)"')
def the_local_prediction_is(step, prediction):
    if isinstance(world.local_prediction, list):
        local_prediction = world.local_prediction[0]
    else:
        local_prediction = world.local_prediction
    try:
        local_model = world.local_model
        if local_model.tree.regression:
            local_prediction = round(float(local_prediction), 4)
            prediction = round(float(prediction), 4)
    except:
        local_model = world.local_ensemble.multi_model.models[0]
        if local_model.tree.regression:
            local_prediction = round(float(local_prediction), 4)
            prediction = round(float(prediction), 4)

    assert local_prediction == prediction


@step(r'the confidence for the local prediction is "(.*)"')
def the_local_prediction_confidence_is(step, confidence):
    local_confidence = world.local_prediction[1]
    local_confidence = round(float(local_confidence), 4)
    confidence = round(float(confidence), 4)
    assert local_confidence == confidence


@step(r'I create a local multi model')
def i_create_a_local_multi_model(step):
    world.local_model = MultiModel(world.list_of_models)

@step(r'I create a batch prediction for "(.*)" and save it in "(.*)"')
def i_create_a_batch_prediction(step, input_data_list, directory):
    if len(directory) > 0 and not os.path.exists(directory):
        os.makedirs(directory)
    input_data_list = eval(input_data_list)
    assert isinstance(input_data_list, list)
    world.local_model.batch_predict(input_data_list, directory)

@step(r'I combine the votes in "(.*)"')
def i_combine_the_votes(step, directory):
    world.votes = world.local_model.batch_votes(directory)

@step(r'the plurality combined predictions are "(.*)"')
def the_plurality_combined_prediction(step, predictions):
    predictions = eval(predictions)
    for i in range(len(world.votes)):
        combined_prediction = world.votes[i].combine()
        assert combined_prediction == predictions[i]

@step(r'the confidence weighted predictions are "(.*)"')
def the_confidence_weighted_prediction(step, predictions):
    predictions = eval(predictions)
    for i in range(len(world.votes)):
        combined_prediction = world.votes[i].combine(1)
        assert combined_prediction == predictions[i]
