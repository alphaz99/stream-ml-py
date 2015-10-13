import sys
from os import path
sys.path.append( path.abspath('./STREAMS_local_dynamic_window/STREAMS_CODE/' ) )

from ML import Stream_Learn, Geomap

from functools import partial
from Stream import Stream, _no_value
from Agent import *
from Operators import stream_func

import numpy as np

import time

import tweepy
from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
import json

import pickle
import pdb

import nltk

import nltk.classify.util
from nltk.classify import NaiveBayesClassifier
from nltk.corpus import movie_reviews
from nltk.stem.porter import *

access_token = "3286035757-eZ7hCq2z05lIfXDZlpzVwGZXRtWlDpQY2Ay9OGr"
access_token_secret = "ZE6vYdbYxXGFTNtsZ4dYELMzsyictDSYzhIu3KfONrlRT"
consumer_key = "aJ68lwHUGqD2TGqYDteYmPbZY"
consumer_secret = "I1GLYYyNF6nNWASzGrq6YV4cPwah5T10eRwnYqLxKCkR6kAYWB"

x = Stream('x')

class StdOutListener(StreamListener):

    def on_data(self, data):
        try:
            data_json = json.loads(data)
            text = data_json['text']
            if data_json['place']['bounding_box'] and 'retweeted_status' not in data_json.keys():
                if data_json['place']['country'] == 'United States':
                    location = np.array(data_json['place']['bounding_box']['coordinates'])
                    location = location.flatten().reshape(4,2)
                    mean_loc = tuple(np.mean(location, 0).tolist())
                    x.extend([(text, float(mean_loc[1]), float(mean_loc[0]))])
        except:
            pass
        return True

    def on_error(self, status):
        print status



def all_func(x, y, model, state, window_state):
    if state is None:
        state = Geomap.Geomap(llcrnrlat = 20, llcrnrlon = -126, urcrnrlat = 60, urcrnrlon = -65)
        state.f.canvas.mpl_connect('draw_event', on_draw)
    locations = np.zeros((len(y), 2))
    for i in range(0, len(y)):
        locations[i][0] = float(y[i][0])
        locations[i][1] = float(y[i][1])

    index = np.zeros((len(y), 1))
    for i in range(0, len(x)):
        tweet = x[i][0]
        sentiment = model.classify(word_feats(tweet.split()))
        index[i] = int(sentiment == 'pos')
    state.clear()
    state.plot(locations, index, text = x, s = 100)

    return state


def train_function(x, y, model, window_state):

    if not model:
        negids = movie_reviews.fileids('neg')
        posids = movie_reviews.fileids('pos')

        negfeats = [(word_feats(movie_reviews.words(fileids=[f])), 'neg') for f in negids]
        posfeats = [(word_feats(movie_reviews.words(fileids=[f])), 'pos') for f in posids]

        negcutoff = len(negfeats)*3/4
        poscutoff = len(posfeats)*3/4

        trainfeats = negfeats[:negcutoff] + posfeats[:poscutoff]
        testfeats = negfeats[negcutoff:] + posfeats[poscutoff:]
        print 'train on %d instances, test on %d instances' % (len(trainfeats), len(testfeats))

        classifier = NaiveBayesClassifier.train(trainfeats)
        print 'accuracy:', nltk.classify.util.accuracy(classifier, testfeats)

        return classifier

    return model

def predict_function(tweet, y, classifier):
    tweet = tweet[0]
    print "--------------------------------------------------------------------------------"
    print "Tweet: ", tweet
    sentiment = classifier.classify(word_feats(tweet.split()))
    if sentiment == 'pos':
        sentiment_r = "Positive"
    elif sentiment == 'neg':
        sentiment_r = "Negative"
    print "Sentiment: ", sentiment_r


def word_feats(words):
    return dict([(word, True) for word in words])

def on_draw(event):
    """Auto-wraps all text objects in a figure at draw-time"""
    import matplotlib as mpl
    fig = event.canvas.figure

    # Cycle through all artists in all the axes in the figure
    for ax in fig.axes:
        for artist in ax.get_children():
            # If it's a text artist, wrap it...
            if isinstance(artist, mpl.text.Text):
                autowrap_text(artist, event.renderer)

    # Temporarily disconnect any callbacks to the draw event...
    # (To avoid recursion)
    func_handles = fig.canvas.callbacks.callbacks[event.name]
    fig.canvas.callbacks.callbacks[event.name] = {}
    # Re-draw the figure..
    fig.canvas.draw()
    # Reset the draw event callbacks
    fig.canvas.callbacks.callbacks[event.name] = func_handles

def autowrap_text(textobj, renderer):
    """Wraps the given matplotlib text object so that it exceed the boundaries
    of the axis it is plotted in."""
    import textwrap
    # Get the starting position of the text in pixels...
    x0, y0 = textobj.get_transform().transform(textobj.get_position())
    # Get the extents of the current axis in pixels...
    clip = textobj.get_axes().get_window_extent()
    # Set the text to rotate about the left edge (doesn't make sense otherwise)
    textobj.set_rotation_mode('anchor')

    # Get the amount of space in the direction of rotation to the left and
    # right of x0, y0 (left and right are relative to the rotation, as well)
    rotation = textobj.get_rotation()
    right_space = min_dist_inside((x0, y0), rotation, clip)
    left_space = min_dist_inside((x0, y0), rotation - 180, clip)

    # Use either the left or right distance depending on the horiz alignment.
    alignment = textobj.get_horizontalalignment()
    if alignment is 'left':
        new_width = right_space
    elif alignment is 'right':
        new_width = left_space
    else:
        new_width = 2 * min(left_space, right_space)

    # Estimate the width of the new size in characters...
    aspect_ratio = 0.5 # This varies with the font!!
    fontsize = textobj.get_size()
    pixels_per_char = aspect_ratio * renderer.points_to_pixels(fontsize)

    # If wrap_width is < 1, just make it 1 character
    wrap_width = max(1, new_width // pixels_per_char)
    try:
        wrapped_text = textwrap.fill(textobj.get_text(), wrap_width)
    except TypeError:
        # This appears to be a single word
        wrapped_text = textobj.get_text()
    textobj.set_text(wrapped_text)

def min_dist_inside(point, rotation, box):
    """Gets the space in a given direction from "point" to the boundaries of
    "box" (where box is an object with x0, y0, x1, & y1 attributes, point is a
    tuple of x,y, and rotation is the angle in degrees)"""
    from math import sin, cos, radians
    x0, y0 = point
    rotation = radians(rotation)
    distances = []
    threshold = 0.0001
    if cos(rotation) > threshold:
        # Intersects the right axis
        distances.append((box.x1 - x0) / cos(rotation))
    if cos(rotation) < -threshold:
        # Intersects the left axis
        distances.append((box.x0 - x0) / cos(rotation))
    if sin(rotation) > threshold:
        # Intersects the top axis
        distances.append((box.y1 - y0) / sin(rotation))
    if sin(rotation) < -threshold:
        # Intersects the bottom axis
        distances.append((box.y0 - y0) / sin(rotation))
    return min(distances)



l = StdOutListener()
auth = OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
stream = tweepy.Stream(auth, l)

model = Stream_Learn(x, x, train_function, predict_function, 1, 10, 1, 1, all_func = all_func)

y = model.run()



stream.filter(track=['trump', 'clinton'], languages=['en'])
# stream.sample(languages=['en'])
