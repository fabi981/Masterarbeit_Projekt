# -*- coding: utf-8 -*-
#Imports
from h11 import SERVER

import dash
from dash import Dash, html, dcc, Input, Output, State, no_update, callback_context, ctx
import dash.dash_table
from dash.exceptions import NonExistentEventException, PreventUpdate
import dash_bootstrap_components as dbc
from dash_canvas import DashCanvas

from flask import Flask, request, jsonify, session, render_template_string, redirect, copy_current_request_context
from socketio import Client

import os

import threading
import requests

import logging#_Verbesserung
from datetime import datetime #_Verbesserung

#from transformers import pipeline


##########Rausgeschmissene Bibliotheken - erstmal nicht benutzt
#import flask_socketio
#from flask_socketio import SocketIO
#import socketio
#from flask_session import Session

#import redis

#import sys
#import io
#import uuid
#import time
#from datetime import timedelta
#import re

#import multiprocessing
#from queue import Queue

#import webbrowser

#import numpy as np
#import matplotlib.pyplot as plt
#from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

#import tkinter as tk
#from tkinter import messagebox
#import cv2
#from PIL import Image, ImageTk
#import base64
#import sounddevice as sd
#import soundfile as sf
#from PyQt6 import QtWidgets
#import librosa
#import librosa.display
#import plotly.graph_objs as go

import logging
from datetime import datetime


####################Logging Methoden
def create_logger(filename):
    logger = logging.getLogger(filename)
    logger.setLevel(logging.INFO)

    if not any(isinstance(handler, logging.FileHandler) and handler.baseFilename == filename for handler in logger.handlers): #<-- musste veraendert werden, um Duplikate zu vermeiden
        handler = logging.FileHandler(filename, mode='a')
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        
        logger.addHandler(handler)
    return logger

# Funktion zum Loggen von Interaktionen
#Element-IDs: JUMP_TO_PAGE, JUMP_TO_CHAPTER, Login-Status, Button_Inpage-Klick, Textfield-Update, Checkbox-Update, 
#Zeichenfenster-Oeffnung, Zeichenfenster-Ohne-KS-Oeffnung, Audiofenster-Oeffnung, YT-Kommentaranalyse-Fenster-Oeffnung
#Zeichenfenster-Schliessung, Zeichenfenster-Ohne-KS-Schliessung, Audiofenster-Schliessung, YT-Kommentaranalyse-Fenster-Schliessung
def log_interaction(user_id = None, element_id = "kein_Element", value = "kein_Wert"):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    if user_id:
        filename = f"user_{user_id}.log"
        logger = create_logger(filename)
        logger.info(f"{timestamp} - Benutzer: {user_id} - Element:'{element_id}' - Value:  '{value}'")
        print("log_interaction: Erfolgreich geloggt!!!!!")
    else:
        filename = "nicht_eingeloggt.log"
        logger = create_logger(filename)
        logger.info(f"{timestamp} - Benutzer: {user_id} - Element:'{element_id}' - Value:  '{value}'")
        print("log_interaction: Erfolgreich geloggt!!!!!")



#################### Globale Datenstrukturen und Variablen, die die Struktur der Dash App bestimmen 
#IP-Adresse des Servers
host_ip = "http://188.245.219.175"
dash_port = "8050"
flask_port = "5000"

#####Globale Datenstrukturen und Variablen: Debug-Methoden
def platzhaltermethode():
    print("Hallo Moto")


# Springt via Flask_Redirecting zur richtigen Dash-Seite. D.h. geht z.B. zu :5000/recirect_dash/50 und von da aus zu :8050/50
def jump_to_dash_page(page_number):
    try:
        response = requests.get(f'http://{host_ip}:5000/redirect_dash/{page_number}', allow_redirects=True)
        return response.status_code == 200  # Erfolgreicher Redirect
    except requests.RequestException as e:
        print(f"Fehler beim Request: {e}")
        return False

def jump_to_chapter_1():
    jump_to_dash_page(CHAPTER_MAPPING[1])
def jump_to_chapter_2():
    jump_to_dash_page(CHAPTER_MAPPING[2])
def jump_to_chapter_3():
    jump_to_dash_page(CHAPTER_MAPPING[3])
def jump_to_chapter_4():
    jump_to_dash_page(CHAPTER_MAPPING[4])
def jump_to_chapter_5():
    jump_to_dash_page(CHAPTER_MAPPING[5])
def jump_to_chapter_6():
    jump_to_dash_page(CHAPTER_MAPPING[6])
def jump_to_chapter_7():
    jump_to_dash_page(CHAPTER_MAPPING[7])
def jump_to_chapter_8():
    jump_to_dash_page(CHAPTER_MAPPING[8])


#####Globale Variablen - Dash
# Verzeichnis zu den Bildern (die 130 PDF-Seiten, die der Hintergrund sind)
ASSETS_DIR = "./pages_9"

# Alle Bilddateien im Verzeichnis: Haben das Format Aufgabe3-1.png, Aufgabe3-2.png, usw.
files = os.listdir(ASSETS_DIR) if os.path.exists(ASSETS_DIR) else []
files = sorted([f for f in files if f.startswith("Aufgabe3") and f.endswith(".png")])
MAX_PAGES = len(files)  # Anzahl der Seiten basierend auf den Dateien

if not MAX_PAGES:
    raise FileNotFoundError("Keine gueltigen Seiten im Verzeichnis gefunden!")

#Kapitel-Mapping: Kapitelnummer -> Seitennummer
CHAPTER_MAPPING = {
    1: 4,
    2: 15,
    3: 23,
    4: 45,
    5: 72,
    6: 84,
    7: 99,
    8: 114,
    9: 121 
}

#Um auf Seite 2 die vertikalen Positionen festzulegen
PAGE2_NAVIGATION_BUTTONS = {
    1: 13.2,
    2: 16.0,
    3: 18.8,
    4: 21.6,
    5: 24.4,
    6: 27.2,
    7: 30.0,
    8: 32.8
}

# Textfeld-Mapping: Textfelder mit IDs; Seitenzahl -> Textfeld-ID -> Koordinaten/Breiten/Hoehen 
# (X/Y/B/H sind prozental im Div festgelegt)
TEXT_FIELDS = {
    5: [
        {"id": "text-5-1", "value": None, "x": 20, "y": 58.9, "width": 35, "height": 18.0, "changable": True},
        {"id": "text-5-2", "value": None, "x": 35, "y": 82.2, "width": 35, "height": 18.0, "changable": True},
        {"id": "text-5-3", "value": None, "x": 48, "y": 58.1, "width": 35, "height": 18.0, "changable": True},
        {"id": "text-5-4", "value": None, "x": 48, "y": 82.1, "width": 35, "height": 18.0, "changable": True},
        {"id": "text-5-5", "value": None, "x": 60, "y": 62.3, "width": 35, "height": 18.0, "changable": True},
        {"id": "text-5-6", "value": None, "x": 62, "y": 82.4, "width": 35, "height": 18.0, "changable": True},
        {"id": "text-5-7", "value": None, "x": 70, "y": 59.2, "width": 35, "height": 18.0, "changable": True},

        {"id": "text-5-8", "value": None, "x": 52, "y": 100, "width": 95, "height": 38.0, "changable": True},#_VERBESSERUNG
    ],
    6: [
        {"id": "text-6-1", "value": None, "x": 58, "y": 72.3, "width": 50, "height": 18.0, "changable": True},
        {"id": "text-6-2", "value": None, "x": 48, "y": 77.5, "width": 50, "height": 18.0, "changable": True},
        {"id": "text-6-3", "value": None, "x": 71, "y": 83, "width": 50, "height": 18.0, "changable": True},

        {"id": "text-6-4", "value": None, "x": 68.2, "y": 42.8, "width": 32.5, "height": 15.0, "changable": True},
        {"id": "text-6-5", "value": None, "x": 75.6, "y": 45.2, "width": 35, "height": 15.0, "changable": True},
        {"id": "text-6-6", "value": None, "x": 44.6, "y": 50.5, "width": 36, "height": 15.0, "changable": True},
        {"id": "text-6-7", "value": None, "x": 34.9, "y": 56, "width": 34, "height": 15.0, "changable": True},
        {"id": "text-6-8", "value": None, "x": 52.3, "y": 56, "width": 36, "height": 15.0, "changable": True},
        {"id": "text-6-9", "value": None, "x": 21.3, "y": 58.4, "width": 33.2, "height": 15.0, "changable": True},
    ],
    8: [
        {"id": "text-8-1", "value": None, "x": 37, "y": 91, "width": 65, "height": 58.0, "changable": True},
    ],
    10: [#_Verbesserung
        {"id": "text-10-1", "value": None, "x": 47, "y": 52, "width": 40, "height": 15.0, "changable": True},
        {"id": "text-10-2", "value": None, "x": 41, "y": 55, "width": 40, "height": 15.0, "changable": True},
        {"id": "text-10-3", "value": None, "x": 44, "y": 58, "width": 40, "height": 15.0, "changable": True},
        {"id": "text-10-4", "value": None, "x": 67, "y": 60, "width": 40, "height": 15.0, "changable": True},
        {"id": "text-10-5", "value": None, "x": 54, "y": 63, "width": 40, "height": 15.0, "changable": True},
        {"id": "text-10-6", "value": None, "x": 47, "y": 66, "width": 40, "height": 15.0, "changable": True},
    ],
    16: [
        {"id": "text-16-1", "value": None, "x": 51, "y": 43, "width": 93, "height": 25.0, "changable": True},
        {"id": "text-16-2", "value": None, "x": 51, "y": 54, "width": 93, "height": 25.0, "changable": True},
        {"id": "text-16-3", "value": None, "x": 51, "y": 65, "width": 93, "height": 25.0, "changable": True},
        {"id": "text-16-4", "value": None, "x": 51, "y": 81, "width": 93, "height": 35.0, "changable": True},
    ],
    18: [
        {"id": "text-18-1", "value": "Stell dir vor, hier waeren deine Audiodaten klassifiziert worden.", "x": 37, "y": 21, "width": 65, "height": 18.0, "changable": False},
    ],
    20: [ # hier pruefen, ob es jetzt auf Seite 17 oder Seite 20 ist.
        {"id": "text-20-1", "value": None, "x": 51, "y": 61, "width": 93, "height": 27.0, "changable": True},
        {"id": "text-20-2", "value": None, "x": 51, "y": 74.5, "width": 93, "height": 27.0, "changable": True},
        {"id": "text-20-3", "value": None, "x": 51, "y": 90, "width": 93, "height": 31.0, "changable": True},
        {"id": "text-20-4", "value": None, "x": 51, "y": 106.4, "width": 93, "height": 31.0, "changable": True},
        {"id": "text-20-5", "value": "Stell dir vor, hier waeren deine Audiodaten klassifiziert worden.", "x": 37, "y": 21, "width": 65, "height": 18.0, "changable": False},

    ],
    21: [ #hier pruefen, ob es jetzt auf Seite 18 oder auf Seite 20 oder auf Seite 21 ist.
        {"id": "text-21-3", "value": None, "x": 51.2, "y": 86, "width": 94.6, "height": 60.0, "changable": True},
    ],
    25: [#hier pruefen, ob jetzt Seite 23 oder 25
        {"id": "text-25-1", "value": None, "x": 32, "y": 39.2, "width": 35, "height": 18.0, "changable": True},
        {"id": "text-25-2", "value": None, "x": 32, "y": 42.2, "width": 35, "height": 18.0, "changable": True},
        {"id": "text-25-3", "value": None, "x": 32, "y": 45.2, "width": 35, "height": 18.0, "changable": True},
        {"id": "text-25-4", "value": None, "x": 32, "y": 47.8, "width": 35, "height": 18.0, "changable": True},
    ],
    27: [#hier pruefen, ob jetzt Seite 25 oder 27
        {"id": "text-27-1", "value": None, "x": 83.5, "y": 55.4, "width": 25, "height": 18.0, "changable": True},
        {"id": "text-27-2", "value": None, "x": 83.5, "y": 60.9, "width": 25, "height": 18.0, "changable": True},
        {"id": "text-27-3", "value": None, "x": 83.5, "y": 66.4, "width": 25, "height": 18.0, "changable": True},
        {"id": "text-27-4", "value": None, "x": 83.5, "y": 71.9, "width": 25, "height": 18.0, "changable": True},
        {"id": "text-27-5", "value": None, "x": 83.5, "y": 76.4, "width": 25, "height": 18.0, "changable": True},
        {"id": "text-27-6", "value": None, "x": 91, "y": 55.4, "width": 25, "height": 18.0, "changable": True},
        {"id": "text-27-7", "value": None, "x": 91, "y": 60.9, "width": 25, "height": 18.0, "changable": True},
        {"id": "text-27-8", "value": None, "x": 91, "y": 66.4, "width": 25, "height": 18.0, "changable": True},
        {"id": "text-27-9", "value": None, "x": 91, "y": 71.9, "width": 25, "height": 18.0, "changable": True},
        {"id": "text-27-10", "value": None, "x": 91, "y": 76.4, "width": 25, "height": 18.0, "changable": True},
    ],
    29: [#pruefen ob 27 oder 29
        {"id": "text-29-1", "value": None, "x": 60.5, "y": 82.4, "width": 22, "height": 18.0, "changable": True},
        {"id": "text-29-2", "value": None, "x": 60.5, "y": 86.9, "width": 22, "height": 18.0, "changable": True},
        {"id": "text-29-3", "value": None, "x": 66.5, "y": 82.4, "width": 22, "height": 18.0, "changable": True},
        {"id": "text-29-4", "value": None, "x": 66.5, "y": 86.9, "width": 22, "height": 18.0, "changable": True},
    ],
    30: [#pruefen ob 28 oder 30
        {"id": "text-30-1", "value": None, "x": 70.5, "y": 33.8, "width": 22, "height": 18.0, "changable": True},
        {"id": "text-30-2", "value": None, "x": 70.5, "y": 38.8, "width": 22, "height": 18.0, "changable": True},
        {"id": "text-30-3", "value": None, "x": 70.5, "y": 43.8, "width": 22, "height": 18.0, "changable": True},
        {"id": "text-30-4", "value": None, "x": 76.8, "y": 33.8, "width": 22, "height": 18.0, "changable": True},
        {"id": "text-30-5", "value": None, "x": 76.8, "y": 38.8, "width": 22, "height": 18.0, "changable": True},
        {"id": "text-30-6", "value": None, "x": 76.8, "y": 43.8, "width": 22, "height": 18.0, "changable": True},
        {"id": "text-30-7", "value": None, "x": 83.1, "y": 33.8, "width": 22, "height": 18.0, "changable": True},
        {"id": "text-30-8", "value": None, "x": 83.1, "y": 38.8, "width": 22, "height": 18.0, "changable": True},
        {"id": "text-30-9", "value": None, "x": 83.1, "y": 43.8, "width": 22, "height": 18.0, "changable": True},
        {"id": "text-30-10", "value": None, "x": 89.5, "y": 33.8, "width": 22, "height": 18.0, "changable": True},
        {"id": "text-30-11", "value": None, "x": 89.5, "y": 38.8, "width": 22, "height": 18.0, "changable": True},
        {"id": "text-30-12", "value": None, "x": 89.5, "y": 43.8, "width": 22, "height": 18.0, "changable": True},

        {"id": "text-30-13", "value": None, "x": 69, "y": 58.3, "width": 22, "height": 18.0, "changable": True},
        {"id": "text-30-14", "value": None, "x": 69, "y": 63.3, "width": 22, "height": 18.0, "changable": True},
        {"id": "text-30-15", "value": None, "x": 69, "y": 68.3, "width": 22, "height": 18.0, "changable": True},
        {"id": "text-30-16", "value": None, "x": 75.3, "y": 58.3, "width": 22, "height": 18.0, "changable": True},
        {"id": "text-30-17", "value": None, "x": 75.3, "y": 63.3, "width": 22, "height": 18.0, "changable": True},
        {"id": "text-30-18", "value": None, "x": 75.3, "y": 68.3, "width": 22, "height": 18.0, "changable": True},
        {"id": "text-30-19", "value": None, "x": 81.6, "y": 58.3, "width": 22, "height": 18.0, "changable": True},
        {"id": "text-30-20", "value": None, "x": 81.6, "y": 63.3, "width": 22, "height": 18.0, "changable": True},
        {"id": "text-30-21", "value": None, "x": 81.6, "y": 68.3, "width": 22, "height": 18.0, "changable": True},
    ],
    35: [#pruefen ob 35 oder 39
        {"id": "text-35-1", "value": None, "x": 48, "y": 40, "width": 30, "height": 18.0, "changable": True},
        {"id": "text-35-2", "value": None, "x": 48, "y": 43.5, "width": 30, "height": 18.0, "changable": True},
        {"id": "text-35-3", "value": None, "x": 48, "y": 47, "width": 30, "height": 18.0, "changable": True},
    ],
    37: [#pruefen ob Seitenzahl passt
        {"id": "text-37-1", "value": None, "x": 30, "y": 43, "width": 30, "height": 18.0, "changable": True},
    ],
    42: [#pruefen ob Seitenzahl passt
        {"id": "text-42-1", "value": None, "x": 33, "y": 56.2, "width": 30, "height": 18.0, "changable": True},
    ],
    43: [#pruefen ob Seitenzahl passt
        {"id": "text-43-1", "value": None, "x": 52.5, "y": 37.5, "width": 95, "height": 30.0, "changable": True},

        {"id": "text-43-2", "value": None, "x": 30, "y": 63, "width": 25, "height": 18.0, "changable": True},
        {"id": "text-43-3", "value": None, "x": 38, "y": 63, "width": 25, "height": 18.0, "changable": True},
        {"id": "text-43-4", "value": None, "x": 46, "y": 63, "width": 25, "height": 18.0, "changable": True},
        {"id": "text-43-5", "value": None, "x": 54, "y": 63, "width": 25, "height": 18.0, "changable": True},
        {"id": "text-43-6", "value": None, "x": 62, "y": 63, "width": 25, "height": 18.0, "changable": True},
    ],
    44: [#pruefen ob Seitenzahl passt
        {"id": "text-44-1", "value": '4', "x": 31, "y": 95, "width": 25, "height": 18.0, "changable": False},
        {"id": "text-44-2", "value": '0', "x": 39, "y": 95, "width": 25, "height": 18.0, "changable": False}, 
        {"id": "text-44-3", "value": '0', "x": 47, "y": 95, "width": 25, "height": 18.0, "changable": False},
        {"id": "text-44-4", "value": '-1', "x": 55, "y": 95, "width": 25, "height": 18.0, "changable": False},
        {"id": "text-44-5", "value": '2', "x": 63, "y": 95, "width": 25, "height": 18.0, "changable": False},
    ],
    49: [#pruefen ob Seitenzahl passt
        {"id": "text-49-1", "value": None, "x": 52.5, "y": 43, "width": 95, "height": 35.0, "changable": True},
        {"id": "text-49-2", "value": None, "x": 52.5, "y": 67.5, "width": 95, "height": 45.0, "changable": True},
    ],
    50: [#pruefen ob Seitenzahl passt
        {"id": "text-50-1", "value": None, "x": 52.5, "y": 40, "width": 95, "height": 35.0, "changable": True},
        {"id": "text-50-2", "value": None, "x": 52.5, "y": 62, "width": 95, "height": 45.0, "changable": True},
    ],
    51: [#pruefen ob Seitenzahl passt
        {"id": "text-51-1", "value": None, "x": 43.5, "y": 59, "width": 80, "height": 60.0, "changable": True},
    ],
    65: [#pruefen ob Seitenzahl passt
        {"id": "text-65-1", "value": None, "x": 52, "y": 80.5, "width": 95, "height": 55.0, "changable": True},
    ],
    69: [#pruefen ob Seitenzahl passt
        {"id": "text-69-1", "value": None, "x": 65, "y": 66, "width": 77.5, "height": 16.0, "changable": True},
        {"id": "text-69-2", "value": None, "x": 65, "y": 71.5, "width": 77.5, "height": 16.0, "changable": True},
        {"id": "text-69-3", "value": None, "x": 67, "y": 78, "width": 76, "height": 18.0, "changable": True},
        {"id": "text-69-4", "value": None, "x": 51.4, "y": 103, "width": 95, "height": 25.0, "changable": True},
    ],
    93: [#pruefen ob Seitenzahl passt
        {"id": "text-93-1", "value": None, "x": 55, "y": 39.5, "width": 23, "height": 18.0, "changable": True},
        {"id": "text-93-2", "value": None, "x": 23.3, "y": 47.7, "width": 23, "height": 18.0, "changable": True},
        {"id": "text-93-3", "value": None, "x": 52, "y": 56, "width": 23, "height": 18.0, "changable": True},
        {"id": "text-93-4", "value": None, "x": 49, "y": 64, "width": 23, "height": 18.0, "changable": True},
        {"id": "text-93-5", "value": None, "x": 47, "y": 72, "width": 23, "height": 18.0, "changable": True},
        {"id": "text-93-6", "value": None, "x": 64, "y": 80, "width": 23, "height": 18.0, "changable": True},
        {"id": "text-93-7", "value": None, "x": 46, "y": 98, "width": 80, "height": 20.0, "changable": True},
    ],
    94: [#pruefen ob Seitenzahl passt
        {"id": "text-94-1", "value": None, "x": 40, "y": 38, "width": 70, "height": 30.0, "changable": True},
        {"id": "text-94-2", "value": None, "x": 88, "y": 80, "width": 25, "height": 17.0, "changable": True},

        {"id": "text-94-3", "value": None, "x": 40, "y": 50, "width": 70, "height": 26.0, "changable": True},
    ],
    96: [#pruefen ob Seitenzahl passt
        {"id": "text-96-1", "value": None, "x": 29.5, "y": 72, "width": 20, "height": 18.0, "changable": True},
        {"id": "text-96-2", "value": None, "x": 37.5, "y": 72, "width": 20, "height": 18.0, "changable": True},
        {"id": "text-96-3", "value": None, "x": 45.5, "y": 72, "width": 20, "height": 18.0, "changable": True},
        {"id": "text-96-4", "value": None, "x": 54, "y": 72, "width": 20, "height": 18.0, "changable": True},
    ],
    100: [
        {"id": "text-100-1", "value": None, "x": 60, "y": 45, "width": 80, "height": 30.0, "changable": True},
    ],
}

# Checkboxes-Mapping: Checkboxen mit IDs; Seitenzahl -> Checkbox-ID -> Koordinaten/Skalierung/anfaenglicher Checked-Zustand 
# (X/Y/S sind prozental im Div festgelegt)
CHECK_BOXES = {
    13: [
        {"id": "checkbox-13-1", "x": 10, "y": 80.5, "scale": 2.5, "checked": False, "changable": True},
        {"id": "checkbox-13-2", "x": 10, "y": 83.2, "scale": 2.5, "checked": False, "changable": True},
        {"id": "checkbox-13-3", "x": 10, "y": 86, "scale": 2.5, "checked": False, "changable": True},
        {"id": "checkbox-13-4", "x": 10, "y": 88.8, "scale": 2.5, "checked": False, "changable": True},
    ],
    42: [
        {"id": "checkbox-42-1", "x": 50, "y": 23.5, "scale": 2.5, "checked": False, "changable": True},
        {"id": "checkbox-42-2", "x": 50, "y": 26.2, "scale": 2.5, "checked": False, "changable": True},
        {"id": "checkbox-42-3", "x": 50, "y": 29, "scale": 2.5, "checked": False, "changable": True},
        {"id": "checkbox-42-4", "x": 50, "y": 31.8, "scale": 2.5, "checked": False, "changable": True},
    ],
    #43: [
    #    {"id": "checkbox-43-1", "x": 60, "y": 37, "scale": 2.5, "checked": False, "changable": True},
    #    {"id": "checkbox-43-2", "x": 60, "y": 39.8, "scale": 2.5, "checked": False, "changable": True},
    #    {"id": "checkbox-43-3", "x": 60, "y": 42.7, "scale": 2.5, "checked": False, "changable": True},
    #], #Aufgabe wurde entfernt
    44: [
        {"id": "checkbox-44-1", "x": 50, "y": 20.8, "scale": 2.5, "checked": False, "changable": False},
        {"id": "checkbox-44-2", "x": 50, "y": 23.5, "scale": 2.5, "checked": False, "changable": False},
        {"id": "checkbox-44-3", "x": 50, "y": 26.3, "scale": 2.5, "checked": True, "changable": False},
        {"id": "checkbox-44-4", "x": 50, "y": 29.1, "scale": 2.5, "checked": True, "changable": False},
    ],
    83: [
        {"id": "checkbox-83-1", "x": 34, "y": 18, "scale": 2.5, "checked": False, "changable": True},
        {"id": "checkbox-83-2", "x": 15, "y": 23.5, "scale": 2.5, "checked": False, "changable": True},
        {"id": "checkbox-83-3", "x": 50, "y": 29, "scale": 2.5, "checked": False, "changable": True},

        {"id": "checkbox-83-4", "x": 50, "y": 37, "scale": 2.5, "checked": False, "changable": True},
        {"id": "checkbox-83-5", "x": 50, "y": 40, "scale": 2.5, "checked": False, "changable": True},
        {"id": "checkbox-83-6", "x": 50, "y": 43, "scale": 2.5, "checked": False, "changable": True},
    ],
    94: [
        {"id": "checkbox-94-1", "x": 86, "y": 53.5, "scale": 2.5, "checked": False, "changable": True},
        {"id": "checkbox-94-2", "x": 50, "y": 59, "scale": 2.5, "checked": False, "changable": True},
        {"id": "checkbox-94-3", "x": 86, "y": 61.7, "scale": 2.5, "checked": False, "changable": True},
        {"id": "checkbox-94-4", "x": 42, "y": 64.2, "scale": 2.5, "checked": False, "changable": True},

        {"id": "checkbox-94-5", "x": 50, "y": 83.2, "scale": 2.5, "checked": False, "changable": True},
        {"id": "checkbox-94-6", "x": 50, "y": 86, "scale": 2.5, "checked": False, "changable": True},
        {"id": "checkbox-94-7", "x": 50, "y": 88.7, "scale": 2.5, "checked": False, "changable": True},
    ],
    96: [
        {"id": "checkbox-96-1", "x": 70, "y": 23.3, "scale": 2.5, "checked": False, "changable": True},
        {"id": "checkbox-96-2", "x": 70, "y": 26.5, "scale": 2.5, "checked": False, "changable": True},
        {"id": "checkbox-96-3", "x": 70, "y": 28.7, "scale": 2.5, "checked": False, "changable": True},
        {"id": "checkbox-96-4", "x": 70, "y": 31.7, "scale": 2.5, "checked": False, "changable": True},

        {"id": "checkbox-96-5", "x": 75, "y": 45.3, "scale": 2.5, "checked": False, "changable": True},
        {"id": "checkbox-96-6", "x": 87, "y": 48, "scale": 2.5, "checked": False, "changable": True},
        {"id": "checkbox-96-7", "x": 13, "y": 53.3, "scale": 2.5, "checked": False, "changable": True},
        {"id": "checkbox-96-8", "x": 33, "y": 58.8, "scale": 2.5, "checked": False, "changable": True},
    ],
    100: [
        {"id": "checkbox-100-1", "x": 25, "y": 23, "scale": 2.5, "checked": False, "changable": True},
        {"id": "checkbox-100-2", "x": 37.5, "y": 23, "scale": 2.5, "checked": False, "changable": True},
        {"id": "checkbox-100-3", "x": 50, "y": 23, "scale": 2.5, "checked": False, "changable": True},
        {"id": "checkbox-100-4", "x": 62.5, "y": 23, "scale": 2.5, "checked": False, "changable": True},
        {"id": "checkbox-100-5", "x": 75, "y": 23, "scale": 2.5, "checked": False, "changable": True},
    ],
}

# Buttons-Mapping: Buttons mit IDs; Seitenzahl -> Button-ID -> Koordinaten/Skalierung/Label(Text des Buttons)/Color(erfuellt i.M. keinen Zweck)/
# Background_Color(Hintergrundfarbe des Button)/Methode(Bei Button-Klick wird diese aktiviert)
# (X/Y sind prozental im Div festgelegt)
BUTTONS = {
    16: [
        #{"id": "button-16-1", "x": 9.5, "y": 19, "label": "Klick mich", "color": "primary", "background_color" : "grey" , "method": platzhaltermethode},
    ],

    18: [
        #{"id": "button-18-1", "x": 50, "y": 12.5, "label": "Audio Aufnehmen", "color": "success", "background_color" : "grey" , "method": platzhaltermethode},
        #{"id": "button-18-2", "x": 50, "y": 18.5, "label": "Audio Beenden", "color": "success", "background_color" : "grey" , "method": platzhaltermethode},
    ],
    20: [
        #
        #{"id": "button-20-1", "x": 7, "y": 15, "label": "OK", "color": "success", "background_color" : "grey" , "method": platzhaltermethode},
    ],
    21: [ #Zweckloesung: hier mussten ganz viele Unicode Leerzeichen eingefuegt werden, damit der Button laenger gestreckt ist und sich ueber die gesamte URL erstreckt
        {"id": "button-21-1", "x": 20.1, "y": 13.1, "label": "\u2003\u2003\u2003\u2003\u2003\u2003\u2003\u2003\u2003\u2003\u2003\u2003\u2003\u2003\u2003\u2003\u2003", "color": "blue", "background_color" : "rgba(128,128,128,0.5)" , "method": platzhaltermethode},
    ],
    33: [
        #{"id": "button-33-1", "x": 12.5, "y": 18.5, "label": "Zeichenfenster oeffnen", "color": "blue", "background_color" : "grey" , "method": platzhaltermethode},
    ],
    42: [
        #{"id": "button-42-1", "x": 12.5, "y": 43.5, "label": "Zeichenfenster oeffnen", "color": "blue", "background_color" : "grey" , "method": platzhaltermethode},
    ],
    43: [
        #{"id": "button-43-1", "x": 10, "y": 83.5, "label": "Fenster oeffnen", "color": "blue", "background_color" : "grey" , "method": platzhaltermethode},
    ],
    69: [
        #{"id": "button-69-1", "x": 12.5, "y": 83.5, "label": "Zeichenfenster oeffnen", "color": "blue", "background_color" : "grey" , "method": platzhaltermethode},
    ],
    94: [
        {"id": "button-94-1", "x": 10, "y": 34.5, "label": "Analysieren", "color": "blue", "background_color" : "grey" , "method": platzhaltermethode},
    ],
}

TEXT_FIELD_VALUES = {
    5: {
        "text-5-1": None, "text-5-2": None, "text-5-3": None,
        "text-5-4": None, "text-5-5": None, "text-5-6": None,
        "text-5-7": None, "text-5-8": None 
    },
    6: {
        "text-6-1": None, "text-6-2": None, "text-6-3": None,
        "text-6-4": None, "text-6-5": None, "text-6-6": None,
        "text-6-7": None, "text-6-8": None, "text-6-9": None
    },
    8: {
        "text-8-1": None
    },
    10: {#_VERBESSERUNG
        "text-10-1": None, "text-10-2": None, "text-10-3": None,
        "text-10-4": None, "text-10-5": None, "text-10-6": None
    },
    16: {
        "text-16-1": None, "text-16-2": None, "text-16-3": None,
        "text-16-4": None
    },
    18: {
        "text-18-1": "Stell dir vor, hier waere deine Emotion klassifiziert worden."
    },
    20: {
        "text-20-1": None, "text-20-2": None, "text-20-3": None,
        "text-20-4": None, "text-20-5": "Stell dir vor, hier waere deine Emotion klassifiziert worden."
    },
    21: {
        "text-21-3": None
    },
    25: {
        "text-25-1": None, "text-25-2": None, "text-25-3": None,
        "text-25-4": None
    },
    27: {
        "text-27-1": None, "text-27-2": None, "text-27-3": None,
        "text-27-4": None, "text-27-5": None, "text-27-6": None,
        "text-27-7": None, "text-27-8": None, "text-27-9": None,
        "text-27-10": None
    },
    29: {
        "text-29-1": None, "text-29-2": None, "text-29-3": None,
        "text-29-4": None
    },
    30: {
        "text-30-1": None, "text-30-2": None, "text-30-3": None,
        "text-30-4": None, "text-30-5": None, "text-30-6": None,
        "text-30-7": None, "text-30-8": None, "text-30-9": None,
        "text-30-10": None, "text-30-11": None, "text-30-12": None,
        "text-30-13": None, "text-30-14": None, "text-30-15": None,
        "text-30-16": None, "text-30-17": None, "text-30-18": None,
        "text-30-19": None, "text-30-20": None, "text-30-21": None
    },
    35: {
        "text-35-1": None, "text-35-2": None, "text-35-3": None
    },
    37: {
        "text-37-1": None
    },
    42: {
        "text-42-1": None
    },
    43: {
        "text-43-1": None, "text-43-2": None, "text-43-3": None,
        "text-43-4": None, "text-43-5": None, "text-43-6": None
    },
    44: {
        "text-44-1": '4', "text-44-2": '0', "text-44-3": '0',
        "text-44-4": '-1', "text-44-5": '2'
    },
    49: {
        "text-49-1": None, "text-49-2": None
    },
    50: {
        "text-50-1": None, "text-50-2": None
    },
    51: {
        "text-51-1": None
    },
    65: {
        "text-65-1": None
    },
    69: {
        "text-69-1": None, "text-69-2": None, "text-69-3": None,
        "text-69-4": None
    },
    93: {
        "text-93-1": None, "text-93-2": None, "text-93-3": None,
        "text-93-4": None, "text-93-5": None, "text-93-6": None,
        "text-93-7": None
    },
    94: {
        "text-94-1": None, "text-94-2": None, "text-94-3": None
    },
    96: {
        "text-96-1": None, "text-96-2": None, "text-96-3": None,
        "text-96-4": None
    },
    100: {
        "text-100-1": None,
    },
}

CHECK_BOX_VALUES = {
    13: {
        "checkbox-13-1": False,
        "checkbox-13-2": False,
        "checkbox-13-3": False,
        "checkbox-13-4": False
    },
    42: {
        "checkbox-42-1": False,
        "checkbox-42-2": False,
        "checkbox-42-3": False,
        "checkbox-42-4": False
    },
    44: {
        "checkbox-44-1": False,
        "checkbox-44-2": False,
        "checkbox-44-3": True,
        "checkbox-44-4": True
    },
    83: {
        "checkbox-83-1": False,
        "checkbox-83-2": False,
        "checkbox-83-3": False,
        "checkbox-83-4": False,
        "checkbox-83-5": False,
        "checkbox-83-6": False
    },
    94: {
        "checkbox-94-1": False,
        "checkbox-94-2": False,
        "checkbox-94-3": False,
        "checkbox-94-4": False,
        "checkbox-94-5": False,
        "checkbox-94-6": False,
        "checkbox-94-7": False
    },
    96: {
        "checkbox-96-1": False,
        "checkbox-96-2": False,
        "checkbox-96-3": False,
        "checkbox-96-4": False,
        "checkbox-96-5": False,
        "checkbox-96-6": False,
        "checkbox-96-7": False,
        "checkbox-96-8": False
    },
    100: {
        "checkbox-100-1": False,
        "checkbox-100-2": False,
        "checkbox-100-3": False,
        "checkbox-100-4": False,
        "checkbox-100-5": False
    }
}

SESSION_ID_VALUE = None

####################Canvas Zeichenfeld fuer Seite 10 (wird in der create_page Methode ebenfalls ueber die Collapse-Liste appendet)
transparent_image_base64 = "data:image/png;base64,"
canvas_element_seite_10 = canvas_element = DashCanvas(#_VERBESSERUNG
    id='canvas',
    width=3000,
    height=1000,
    hide_buttons=['line', 'zoom', 'pan', 'undo', 'redo', 'fill', 'rect', 'circle', 'poly', 'free', 'select', 'pencil', 'rectangle'],
    goButtonTitle=None,
    lineWidth=3,
    image_content=transparent_image_base64,
)



####################DBC Collapse Elemente fuer Seite 9, die sich oeffnende Texte ermoeglichen - 
##Dash Callbacks ganz unten im Code
collapse_component = dbc.Container(  #_Verbesserung
    [
        dbc.Button(
            "Acetylcholin (ACh) - foerdert Muskelbewegungen und unterstuetzt Gedaechtnis und Aufmerksamkeit",
            id="collapse-button-1",
            className="mb-1 w-100",
            #style={"backgroundColor": "#F7F7F7", "borderColor": "#F7F7F7", "width": "100%"},
            color="secondary",
            n_clicks=0,
        ),
        #style={"width": "100%"},
        #className="d-flex justify-content-center",  # Zentriert 
        dbc.Collapse(
            [
                html.P("Acetylcholin ist ein Neurotransmitter, der bei der Muskelbewegung und in kognitiven Prozessen wie Lernen und Gedaechtnis eine Schluesselrolle spielt. Es wird vom Koerper sowohl im Gehirn als auch in peripheren Nerven verwendet. Spannend ist, dass Acetylcholin ueber verschiedene Rezeptoren unterschiedlich wirken kann - es kann die Herzfrequenz senken oder Muskeln anregen. Nach seiner Freisetzung wird es durch ein Enzym schnell abgebaut, um die Signaluebertragung zu beenden. Diese vielseitige Wirkung zeigt, wie es in einigen Prozessen aktiviert und in anderen gehemmt werden kann."),
            ],
            id="collapse-1",
            style={"border": "1px solid black"},
        ),
        #html.Br(),
        
        dbc.Button(
            "Dopamin - reguliert Belohnung und Motivation und steuert emotionale Reaktionen",
            id="collapse-button-2",
            className="mb-1 w-100",
            #style={"backgroundColor": "#F7F7F7", "borderColor": "#F7F7F7", "width": "100%"},
            color="secondary",
            n_clicks=0,
        ),
        dbc.Collapse(
            [
                html.P("Dopamin ist bekannt dafuer, unser Belohnungssystem zu aktivieren, wenn wir etwas Angenehmes tun, wie ein Stueck Schokolade zu essen. Es ist auch wichtig fuer unsere Motivation und es hilft uns, Bewegungen zu steuern. Gleichzeitig wirkt Dopamin in manchen Bereichen regulierend, indem es die Aktivitaet von Nervenzellen daempft, um Bewegungen praezise zu steuern. Ein Mangel fuehrt zu Bewegungsstoerungen wie Parkinson, waehrend ein Ueberschuss mit Schizophrenie in Verbindung gebracht wird. Die Balance von Dopamin ist daher essentiell fuer das Wohlbefinden und die Gesundheit des Gehirns."),
            ],
            id="collapse-2",
            style={"border": "1px solid black"}
        ),
        #html.Br(),
        
        dbc.Button(
            "Serotonin - reguliert Stimmung und Schlaf und beeinflusst den Appetit",
            id="collapse-button-3",
            className="mb-1 w-100",
            #style={"backgroundColor": "#F7F7F7", "borderColor": "#F7F7F7", "width": "100%"},
            color="secondary",
            n_clicks=0,
        ),
        dbc.Collapse(
            [
                html.P("Serotonin ist ein Neurotransmitter, der unsere Stimmung , den Schlaf und den Appetit reguliert. Es sorgt dafuer, dass wir uns ausgeglichen fuehlen und es ist an vielen Prozessen im Gehirn beteiligt. Interessant ist, dass Serotonin je nach Rezeptor sowohl aktivierend (bei der Unterstuetzung kognitiver Prozesse) als auch beruhigend (bei der Foerderung von Schlaf) wirken kann. Ein Ungleichgewicht kann Depressionen oder Angstzustaende ausloesen. Die vielfaeltige Wirkung mahct Serotonin zu einem wichtigen 'Manager' fuer die Balance von kognitiven Prozessen."),
            ],
            id="collapse-3",
            style={"border": "1px solid black"},
        ),
        #html.Br(),
        
        dbc.Button(
            "Noradrenalin - steuert die 'Fight & Flight'-Reaktion und foerdert Wachsamkeit",
            id="collapse-button-4",
            className="mb-1 w-100",
            #style={"backgroundColor": "#F7F7F7", "borderColor": "#F7F7F7", "width": "100%"},
            color="secondary",
            n_clicks=0,
        ),
        dbc.Collapse(
            [
                html.P("Noradrenalin sorgt dafuer, dass wir wach und aufmerksam bleiben, besonders in stressigen Situationen. Es versetzt unseren Koerper in Alarmbereitschaft und steigert Herzschlag und Atmung, um auf Gefahren vorbereitet zu sein. Gleichzeitig reguliert Noradrenalin auch die Konzentration und hilft uns beim Fokussieren. Diese aktivierende WIrkung ist essenziell fuer unsere 'Fight & Flight'-Reaktion und zeigt, wie es in dynamischen Situationen das Nervensystem antreibt."),
            ],
            id="collapse-4",
            style={"border": "1px solid black"},
        ),
        #html.Br(),
        
        dbc.Button(
            "Gamma-Aminobuttersaeure (GABA) - reduziert Erregung und foerdert Entspannung",
            id="collapse-button-5",
            className="mb-1 w-100",
            #style={"backgroundColor": "#F7F7F7", "borderColor": "#F7F7F7", "width": "100%"},
            color="secondary",
            n_clicks=0,
        ),
        dbc.Collapse(
            [
                html.P("GABA ist der wichtigste Neurotransmitter im Gehirn, um in stressigen Situationen ruhig bleiben zu koennen. Es wirkt wie eine Bremse, die Nervenzellen daran hindert, uebermaessig aktiv zu werden. Besonders interessant ist, dass viele Beruhigungsmittel die Wirkung von GABA verstaerken, wodurch Aengste reduziert werden und der Schlaf gefoerdert wird. Ohne GABA koennte das Gehirn in einen Zustand der Uebererregung geraten. Seine Faehigkeit, uebermaessige Aktivitaet zu hemmen, macht es zu einem Schutzfaktor fuer das Nervensystem."),
            ],
            id="collapse-5",
            style={"border": "1px solid black"},
        ),
        #html.Br(),
        
        dbc.Button(
            "Glutamat - verstaerkt Errregung und spielt eine Schluesselrolle beim Lernen",
            id="collapse-button-6",
            className="mb-1 w-100",
            #style={"backgroundColor": "#F7F7F7", "borderColor": "#F7F7F7", "width": "100%"},
            color="secondary",
            n_clicks=0,
        ),
        dbc.Collapse(
            [
                html.P("Glutamat ist der wichtigste aktivierende Neurotransmitter im Gehirn und sorgt dafuer, dass Nervenzellen Signale weiterleiten koennen. Es ist essenziell, fuer Denkprozesse und das Gedaechtnis. Weiterhin wirkt es ueber spezielle Rezeptoren, die die synaptische Verbindung zwischen Nervenzellen staerken. Zu viel Glutamat kann jedoch schaedlich sein und die Nervenzellen ueberlasten, weshalb der Koerper die Konzentration im System streng kontrolliert. Seine Aufgabe, neuronale Aktivitaet gezielt anzutreiben, macht es zu einem Motor fuer die Informationsverarbeitung im Gehirn."),
            ],
            id="collapse-6",
            style={"border": "1px solid black"},
        ),
        #html.Br(),
        
        dbc.Button(
            "Endorphine - wirken als natuerliches Schmerzmittel und foerdert Gefuehle von Euphorie",
            id="collapse-button-7",
            className="mb-1 w-100",
            #style={"backgroundColor": "#F7F7F7", "borderColor": "#F7F7F7", "width": "100%"},
            color="secondary",
            n_clicks=0,
        ),
        dbc.Collapse(
            [
                html.P("Endorphine sind natuerliche Schmerzmitttel, die in Stresssituationen oder bei intensiver Bewegung wie Laufen freigesetzt werden.  Sie blockieren Schmerzsignaleund foerdern Gefuehle von Freude und Entspannung, man denke z.B. an das 'Runner's High' beim Jogging. Gleichzeitig regulieren Endorphine emotionale Reaktionen und helfen, den Koerper mit Belastungen umzugehen. Durch ihre Faehigkeit, gezielt die Weiterleitung unangenehmer Signale zu blockieren, daempfen sie das Schmerzempfinden."),
            ],
            id="collapse-7",
            style={"border": "1px solid black"},
        ),
        #html.Br(),
        
        dbc.Button(
            "Histamin - reguliert den 'Schlaf-Wach-Rhythmus und steuert Immunreaktionen'",
            id="collapse-button-8",
            className="mb-1 w-100",
            #style={"backgroundColor": "#F7F7F7", "borderColor": "#F7F7F7", "width": "100%"},
            color="secondary",
            n_clicks=0,
        ),
        dbc.Collapse(
            [
                html.P("Histamin ist ein Neurotransmitter, der Achtsamkeit und Konzentration steigert und gleichzeitig Hunger- und Schlafsignale im Gehirn steuert. Es spielt nicht nur bei Allergien eine Rolle, sondern ist auch fuer die Regulation von Appetet und Magensaeureproduktion verantwortlich. Interessant ist, dass Histamin durch diese aktivierenden Funktionen nicht nur die Aufmerksamkeit, sondern auch koerperliche Prozeses wie die Verdauung anregt. Ohne Histamin waeren wir viel weniger aufmerksam und leistungsfaehig."),
            ],
            id="collapse-8",
            style={"border": "1px solid black"},
        ),
    ],
    className="p-5",
)


####################DBC Modale, um kleine Popups zu oeffnen - die Dash-Callbacks zu den Modalen 
##befinden sich ganz unten im Code, kurz vor der __name__ == main
modal_zeichenfenster = dbc.Modal(
    [
        dbc.ModalHeader("Zeichenfenster"),
        dbc.ModalBody(
            html.Iframe(
                src= f"{host_ip}:{flask_port}/zeichenfenster", #HIER IP UEBERARBEITET""http://127.0.0.1:5000/zeichenfenster",
                style={"width": "100%", "height": "500px", "border": "none"}
            )
        ),
        dbc.ModalFooter(
            dbc.Button("Schliessen", id="close-modal", className="ml-auto")
        ),
    ],
    id="zeichenfenster-modal",
    size="xl",  # Groesse waehlbar zwischen: "sm", "lg", "xl"
    #style={
    #    "marginTop": "10%"  # Verschiebt das Modal nach unten
    #},
)
modal_zeichenfenster_ohne_ks = dbc.Modal(
    [
        dbc.ModalHeader("Zeichenfenster"),
        dbc.ModalBody(
            html.Iframe(
                src= f"{host_ip}:{flask_port}/zeichenfenster_ohne_ks", #HIER IP UEBERARBEITET""http://127.0.0.1:5000/zeichenfenster_ohne_ks",
                style={"width": "100%", "height": "600px", "border": "none"}
            )
        ),
        dbc.ModalFooter(
            dbc.Button("Schliessen", id="close-modal", className="ml-auto")
        ),
    ],
    id="zeichenfenster-modal-ohne-ks",
    size="xl",  # Groesse waehlbar zwischen: "sm", "lg", "xl"
)


modal_audioaufnahme = dbc.Modal(
    [
        dbc.ModalHeader("Audioaufnahme"),
        dbc.ModalBody(
            html.Iframe(
                src= f"{host_ip}:{flask_port}/audioaufnahme", #HIER IP UEBERARBEITET""http://127.0.0.1:5000/audioaufnahme",
                style={"width": "100%", "height": "600px", "border": "none"},
                allow="microphone"
            ),
            #html.Div(id="audio-data-output")  # Neue Komponente fuer die Audio-Ausgabe  #keine Zeit mehr, die Pisse zu ueberarberiten
        ),
        dbc.ModalFooter(
            dbc.Button("Schliessen", id="close-modal", className="ml-auto")
        ),
    ],
    id="audioaufnahme-modal",
    size="xl",  # Groesse waehlbar zwischen: "sm", "lg", "xl"
)


modal_yt_kommentaranalyse = dbc.Modal(
    [
        dbc.ModalHeader("YT-Kommentaranalyse"),
        dbc.ModalBody(
            html.Iframe(
                src= f"{host_ip}:{flask_port}/yt_kommentaranalyse", #HIER IP UEBERARBEITET""http://127.0.0.1:5000/yt_kommentaranalyse",
                style={"width": "100%", "height": "600px", "border": "none"},
                #allow="microphone"
            ),
            #html.Div(id="audio-data-output")  # Neue Komponente fuer die Audio-Ausgabe  #keine Zeit mehr, die Pisse zu ueberarberiten
        ),
        dbc.ModalFooter(
            dbc.Button("Schliessen", id="close-modal", className="ml-auto")
        ),
    ],
    id="yt-kommentaranalyse-modal",
    size="xl",  # Groesse waehlbar zwischen: "sm", "lg", "xl"
)

modal_kameraanalyse = dbc.Modal(
    [
        dbc.ModalHeader("YT-Kommentaranalyse"),
        dbc.ModalBody(
            html.Iframe(
                src=f"{host_ip}:{flask_port}/kameraanalse", #HIER IP UEBERARBEITET" "http://127.0.0.1:5000/kameraanalyse",
                style={"width": "100%", "height": "600px", "border": "none"},
                #allow="microphone"
            ),
            #html.Div(id="audio-data-output")  # Neue Komponente fuer die Audio-Ausgabe  #keine Zeit mehr, die Pisse zu ueberarberiten
        ),
        dbc.ModalFooter(
            dbc.Button("Schliessen", id="close-modal", className="ml-auto")
        ),
    ],
    id="kameraanalyse-modal",
    size="xl",  # Groesse waehlbar zwischen: "sm", "lg", "xl"
)




# Fuegen Sie das Modal zu Ihrem Layout hinzu
#app.layout = html.Div([
#    dbc.Button("Zeichenfenster oeffnen", id="open-modal", n_clicks=0),
#    modal
#])



#################### DASH Code
#####Initialisiere die Dash-App, vorher als parameter drin gewesen: server=flask_app
app = Dash(__name__, assets_folder=ASSETS_DIR, suppress_callback_exceptions=True, external_stylesheets=[dbc.themes.BOOTSTRAP])##LETZER PARAMETER WURDE UEBERARBEITET
app_server = app.server

#####Einrichtung des Clients um Daten von Flask zu empfangen
socketio_dashclient = Client()
#Der Client wird ueber die create_page methode gestartet, weil es in der __main__ = name zu massiven Fehlern fuehrt

####Testen erfolgreicher Verbindungsaufbau
@socketio_dashclient.on('connect')
def connect():
    print("connect: Dash-App-Client verbunden.")


#####Basis-Layout der App
app.layout = html.Div([
    #Audio-Store fuer Seite 18
    #dcc.Store(id='audio-data-store'),
    #dcc.Interval(id='audio-data-interval', interval=500, n_intervals=0),

    dcc.Store(id='text-store', data={}, storage_type='memory'),  # Speichert alle Texteingaben; vermutlich redundant, weil im Session-Speicher (+Redis) gespeichert, aber weiss ich gerade nicht genau
    dcc.Location(id='url', refresh=False),  #weiss ich selber nicht mehr, wofuer die Location gut ist
    dcc.Interval(id='update-interval', interval=10000, n_intervals=0),  # Intervall (alle 10000ms) - updatet die Textfeld-Inhalte in diesem Zeitraum

    # Dummy-Output fuer den Button-Callback
    html.Div(id='dummy-output', style={'display': 'none'}), # Dummy Output, der noetig ist, um leere Rueckgaben an Dash zu taetigen. Dash benoetigt immer einen Output
    html.Div(id='dummy-output2', style={'display': 'none'}), #erster war ueberladen
    html.Button(id='dummy-trigger', style={'display': 'none'}, n_clicks=0), #Dummy Trigger, das gleiche, nur fuer die Buttons

    html.Div([
        # Linker Bereich (Seite und Kapitel auswaehlen)
        html.Div([
            html.Div([
                dcc.Input(id='page-input', type='number', min=1, max=MAX_PAGES, placeholder='Seite', style={
                    'width': '70px',
                    'marginRight': '10px',
                    'padding': '5px',
                    'fontSize': '16px',
                    'border': '1px solid #ccc',
                    'borderRadius': '3px'
                }),
                html.Button('Springen', id='jump-button', style={
                    'backgroundColor': '#007bff',
                    'color': 'white',
                    'border': 'none',
                    'padding': '10px 20px',
                    'fontSize': '16px',
                    'borderRadius': '3px',
                    'cursor': 'pointer'
                })
            ], style={'display': 'flex', 'alignItems': 'center', 'marginRight': '20px'}),
            html.Div([
                dcc.Input(id='chapter-input', type='number', min=1, max=len(CHAPTER_MAPPING), placeholder='Kapitel', style={
                    'width': '70px',
                    'marginRight': '10px',
                    'padding': '5px',
                    'fontSize': '16px',
                    'border': '1px solid #ccc',
                    'borderRadius': '3px'
                }),
                html.Button('Zu Kapitel', id='chapter-button', style={
                    'backgroundColor': '#007bff',
                    'color': 'white',
                    'border': 'none',
                    'padding': '10px 20px',
                    'fontSize': '16px',
                    'borderRadius': '3px',
                    'cursor': 'pointer'
                })
            ], style={'display': 'flex', 'alignItems': 'center'})
        ], style={'flex': '1', 'textAlign': 'left', 'paddingLeft': '20px', 'display': 'flex'}),
        #Mittlerer Bereich: Zurueck Weiter
        html.Div([
            html.A('Zurueck', id='back-button', href='/1', style={
                'marginRight': '15px',
                'backgroundColor': '#ddd',
                'color': 'black',
                'border': '1px solid #ccc',
                'padding': '10px 20px',
                'textAlign': 'center',
                'textDecoration': 'none',
                'display': 'inline-block',
                'fontSize': '16px',
                'borderRadius': '3px',
                'cursor': 'pointer'
            }),
            html.A('Weiter', id='forward-button', href='/2', style={
                'backgroundColor': '#ddd',
                'color': 'black',
                'border': '1px solid #ccc',
                'padding': '10px 20px',
                'textAlign': 'center',
                'textDecoration': 'none',
                'display': 'inline-block',
                'fontSize': '16px',
                'borderRadius': '3px',
                'cursor': 'pointer'
            })
        ], style={'flex': '1', 'textAlign': 'center'}),
        #html.Div([], style={'flex': '1', 'textAlign': 'right', 'paddingRight': '20px'}),
        
        #### Neu: Rechter Bereich - Login Logout, Eingeloggt-Text
        html.Div([
            html.Span(children="Nicht eingeloggt!", id = 'login-status', style={
                'marginRight': '10px',
                'fontSize': '16px',
                'color': '#333'
            }),
            html.A('Login', href=f'{host_ip}:{flask_port}/authenticate', style={
            'marginRight': '15px',
            'backgroundColor': '#28a745',
            'color': 'white',
            'border': 'none',
            'padding': '10px 20px',
            'textAlign': 'center',
            'textDecoration': 'none',
            'display': 'inline-block',
            'fontSize': '16px',
            'borderRadius': '3px',
            'cursor': 'pointer'
            }),
            html.A('Session loeschen', href=f'{host_ip}:{flask_port}/clear-session', style={
            'backgroundColor': '#dc3545',
            'color': 'white',
            'border': 'none',
            'padding': '10px 20px',
            'textAlign': 'center',
            'textDecoration': 'none',
            'display': 'inline-block',
            'fontSize': '16px',
            'borderRadius': '3px',
            'cursor': 'pointer'
            })
            ], style={'flex': '1', 'textAlign': 'right', 'paddingRight': '20px'})
        ####


    ], style={
        'position': 'fixed',
        'top': '0',
        'width': '100%',
        'background': 'white',
        'display': 'flex',
        'alignItems': 'center',
        'padding': '10px',
        'boxShadow': '0 2px 4px rgba(0,0,0,0.1)',
        'zIndex': '1000',
    }),
    html.Div(id='page-content', style={'marginTop': '50px', 'width': '100%', 'height': 'calc(100vh - 50px)'})
])


#####Dash: create-page Methode, um einzelne Elemente der Seiten automatisiert zu erzeugen, gemaess der globalen Datenstrukturen und Variablen
def create_page(page_num):
    #Verbindungsaufbau zu host_ip:5000
    if socketio_dashclient.connected:
        print("Der SocketIO-Client ist bereits verbunden.")
    else:
        print("Der SocketIO-Client ist nicht verbunden. host_ip: ", host_ip, " flask_port: ", flask_port)
        socketio_dashclient.connect(f"{host_ip}:{flask_port}")

    navigation_buttons = []
    if page_num == 2:
        for i in range(1, 7): # Auf Seite 2 kann man die Kapitel bis einschliesslich 6 nun direkt anklicken um dahin zu gelangen
            navigation_buttons.append(
                html.Div(
                    html.A(
                        html.Button('', 
                            style={
                                'width': '100%',
                                'height': '100%',
                                'padding': '10px',
                                'fontSize': '16px',
                                'border': '1px solid #ccc',
                                'borderRadius': '5px',
                                'backgroundColor': 'rgba(255, 255, 255, 0.15)',
                                'cursor': 'pointer'
                            }),
                        href=f'/{CHAPTER_MAPPING[i]}'
                    ),
                    style={
                        "position": "absolute",
                        "top": f"{PAGE2_NAVIGATION_BUTTONS[i]}%",
                        "left": "35%",
                        "width": "60%",
                        "height": "2.5%",
                        "transform": "translate(-50%, -50%)",
                    }
                )
            )

    ##### Hier wird das DBC Collapse Element auf Seite 5 erzeugt
    collapse_elemente = [] #_Verbesserung
    if page_num == 9:
        collapse_elemente.append(
            html.Div(
            collapse_component,
            style={"marginTop": "26%"}  # Hier wird der Abstand oben angepasst
            )
        )
    
    ##### Dash Canvas auf Seite 10
    if page_num == 10:
        collapse_elemente.append(
            html.Div(
                canvas_element_seite_10,
                style={
                    "position": "absolute",
                    "top": "24%",
                    "left": "0%",
                    "width": "100%",
                    "height": "50vh",
                }
            )
        )
    
    ##### Hier sind die Buttons fuer die DBC Modale eingebaut
    modal_button_elemente = []
    if page_num == 16:
        modal_button_elemente = [
            html.Div([
                dbc.Button(
                    "Kameraanalyse oeffnen", 
                    id="open-kameraanalyse-modal",
                    n_clicks=0,
                    style={
                        'backgroundColor': 'grey',
                        'color': 'black',
                        'border': 'none',
                        'padding': '10px 20px',
                        'fontSize': '16px',
                        'borderRadius': '5px',
                        'cursor': 'pointer'
                    }
                ),
                modal_kameraanalyse,
            ],
            style={
                "position": "absolute",
                "top": "19%",  # Sie koennen diese Werte anpassen
                "left": "10%",  # Sie koennen diese Werte anpassen
                "transform": "translate(-30%, -30%)"
            })
        ]
    if page_num == 18:
        modal_button_elemente = [
            html.Div([
                dbc.Button(
                    "Audioaufnahme oeffnen", 
                    id="open-audioaufnahme-modal",
                    n_clicks=0,
                    style={
                        'backgroundColor': 'grey',
                        'color': 'black',
                        'border': 'none',
                        'padding': '10px 20px',
                        'fontSize': '16px',
                        'borderRadius': '5px',
                        'cursor': 'pointer'
                    }
                ),
                modal_audioaufnahme,
            ],
            style={
                "position": "absolute",
                "top": "19%",  # Sie koennen diese Werte anpassen
                "left": "10%",  # Sie koennen diese Werte anpassen
                "transform": "translate(-30%, -30%)"
            })
        ]

    #YT Kommentaranalyse oeffnen
    if page_num == 20:
        modal_button_elemente = [
            html.Div([
                dbc.Button(
                    "YT-Kommentaranalse oeffnen", 
                    id="open-yt-kommentaranalyse-modal",
                    n_clicks=0,
                    style={
                        'backgroundColor': 'grey',
                        'color': 'black',
                        'border': 'none',
                        'padding': '10px 20px',
                        'fontSize': '16px',
                        'borderRadius': '5px',
                        'cursor': 'pointer'
                    }
                ),
                modal_yt_kommentaranalyse,
            ],
            style={
                "position": "absolute",
                "top": "19%",  # Sie koennen diese Werte anpassen
                "left": "10%",  # Sie koennen diese Werte anpassen
                "transform": "translate(-30%, -30%)"
            })
        ]

    #Zeichenfeld mit Koordinatensystem
    if page_num == 33:
        modal_button_elemente = [
            html.Div([
                dbc.Button(
                    "Zeichenfenster oeffnen", 
                    id="open-zeichenfenster-modal",
                    n_clicks=0,
                    style={
                        'backgroundColor': 'grey',
                        'color': 'black',
                        'border': 'none',
                        'padding': '10px 20px',
                        'fontSize': '16px',
                        'borderRadius': '5px',
                        'cursor': 'pointer'
                    }
                ),
                modal_zeichenfenster,
            ],
            style={
                "position": "absolute",
                "top": "19%",  # Sie koennen diese Werte anpassen
                "left": "10%",  # Sie koennen diese Werte anpassen
                "transform": "translate(-30%, -30%)"
            })
        ]
    #Zeichenfeld ohne Koordinatensystem
    if page_num == 35:
        modal_button_elemente = [
            html.Div([
                dbc.Button(
                    "Zeichenfenster oeffnen", 
                    id="open-zeichenfenster-modal-ohne-ks",
                    n_clicks=0,
                    style={
                        'backgroundColor': 'grey',
                        'color': 'black',
                        'border': 'none',
                        'padding': '10px 20px',
                        'fontSize': '16px',
                        'borderRadius': '5px',
                        'cursor': 'pointer'
                    }
                ),
                modal_zeichenfenster_ohne_ks,
            ],
            style={
                "position": "absolute",
                "top": "52%",  # 
                "left": "10%",  # 
                "transform": "translate(-30%, -30%)"
            })
        ]
        
    #Zeichenfeld ohne Koordinatensystem
    if page_num == 37:
        modal_button_elemente = [
            html.Div([
                dbc.Button(
                    "Zeichenfenster oeffnen", 
                    id="open-zeichenfenster-modal-ohne-ks",
                    n_clicks=0,
                    style={
                        'backgroundColor': 'grey',
                        'color': 'black',
                        'border': 'none',
                        'padding': '10px 20px',
                        'fontSize': '16px',
                        'borderRadius': '5px',
                        'cursor': 'pointer'
                    }
                ),
                modal_zeichenfenster_ohne_ks,
            ],
            style={
                "position": "absolute",
                "top": "45%",  # Sie koennen diese Werte anpassen
                "left": "10%",  # Sie koennen diese Werte anpassen
                "transform": "translate(-30%, -30%)"
            })
        ]

    if page_num == 42:
        modal_button_elemente = [
            html.Div([
                dbc.Button(
                    "Zeichenfenster oeffnen", 
                    id="open-zeichenfenster-modal",
                    n_clicks=0,
                    style={
                        'backgroundColor': 'grey',
                        'color': 'black',
                        'border': 'none',
                        'padding': '10px 20px',
                        'fontSize': '16px',
                        'borderRadius': '5px',
                        'cursor': 'pointer'
                    }
                ),
                modal_zeichenfenster,
            ],
            style={
                "position": "absolute",
                "top": "48%",  # Sie koennen diese Werte anpassen
                "left": "10%",  # Sie koennen diese Werte anpassen
                "transform": "translate(-30%, -30%)"
            })
        ]

    if page_num == 43:
        modal_button_elemente = [
            html.Div([
                dbc.Button(
                    "Zeichenfenster oeffnen", 
                    id="open-zeichenfenster-modal-ohne-ks",
                    n_clicks=0,
                    style={
                        'backgroundColor': 'grey',
                        'color': 'black',
                        'border': 'none',
                        'padding': '10px 20px',
                        'fontSize': '16px',
                        'borderRadius': '5px',
                        'cursor': 'pointer'
                    }
                ),
                modal_zeichenfenster_ohne_ks,
            ],
            style={
                "position": "absolute",
                "top": "43%",  # Sie koennen diese Werte anpassen
                "left": "10%",  # Sie koennen diese Werte anpassen
                "transform": "translate(-30%, -30%)"
            })
        ]

    if page_num == 69:
        modal_button_elemente = [
            html.Div([
                dbc.Button(
                    "Zeichenfenster oeffnen", 
                    id="open-zeichenfenster-modal",
                    n_clicks=0,
                    style={
                        'backgroundColor': 'grey',
                        'color': 'black',
                        'border': 'none',
                        'padding': '10px 20px',
                        'fontSize': '16px',
                        'borderRadius': '5px',
                        'cursor': 'pointer'
                    }
                ),
                modal_zeichenfenster,
            ],
            style={
                "position": "absolute",
                "top": "83%",  # Sie koennen diese Werte anpassen
                "left": "10%",  # Sie koennen diese Werte anpassen
                "transform": "translate(-30%, -30%)"
            })
        ]


    ##### Hier ist der Umfragebogen fuer die MA eingebaut
    umfrage_elemente = []
    if page_num == 100:
        umfrage_elemente = [
            html.Div([
                html.H1("1. Wissenstest", style={'textAlign': 'center'}),
                html.Div([
                    html.H2("Frage 1: Wissenspruefung 1",style={'textAlign': 'center'}),
                    html.Div([
                        html.Div("stimme zu", style={'flex': '1', 'textAlign': 'center'}),
                        html.Div("stimme eher zu", style={'flex': '1', 'textAlign': 'center'}),
                        html.Div("neutral", style={'flex': '1', 'textAlign': 'center'}),
                        html.Div("stimme eher nicht zu", style={'flex': '1', 'textAlign': 'center'}),
                        html.Div("stimme nicht zu", style={'flex': '1', 'textAlign': 'center'})
                    ], style={'display': 'flex', 'width': '100%', 'margin': '10px auto'}),
                    html.Div("Hier kommen die Checkboxen hin", style={'margin': '20px 0'}),
                ],style={"position": "absolute", "top": "10%", "left": "10%", "width": "80%", "height": "30%"}),

                html.Div([
                    html.H2("Frage 2: Wissenspruefung 2.", style={'textAlign': 'center'}),
                ],style={"position": "absolute", "top": "20%", "left": "10%", "width": "80%", "height": "30%"}),

            ], style={
                "position": "absolute",
                "top": "10%",
                "left": "10%",
                "width": "80%",
                "height": "80%"
            })
        ]
    elif page_num == 101:
        umfrage_elemente = [
            html.Div([
                html.H1("1. Wissenstest", style={'textAlign': 'center'}),
                html.H2("Frage 1: Hier Frage",style={'textAlign': 'center'}),
                html.Div("Hier kommt das Textfeld hin", style={'margin': '20px 0', 'height': '100px', 'border': '1px solid black'}),
                html.H2("Frage 2: Hier Frage", style={'textAlign': 'center'}),
                html.Div("Hier kommt das Textfeld hin", style={'margin': '20px 0', 'height': '100px', 'border': '1px solid black'}),
                html.H2("Frage 2: Hier Frage", style={'textAlign': 'center'}),
                html.Div("Hier kommt das Textfeld hin", style={'margin': '20px 0', 'height': '100px', 'border': '1px solid black'}),
                html.H2("Frage 2: Hier Frage", style={'textAlign': 'center'}),
                html.Div("Hier kommt das Textfeld hin", style={'margin': '20px 0', 'height': '100px', 'border': '1px solid black'}),
                html.H2("Frage 2: Hier Frage", style={'textAlign': 'center'}),
                html.Div("Hier kommt das Textfeld hin", style={'margin': '20px 0', 'height': '100px', 'border': '1px solid black'})
            ], style={
                "position": "absolute",
                "top": "10%",
                "left": "10%",
                "width": "80%",
                "height": "80%"
            })
        ]
    elif page_num == 102:
        umfrage_elemente = [
            html.Div([
                html.H1("1. Wissenstest", style={'textAlign': 'center'}),
                html.H2("Frage: Wie oft nutzen Sie das Produkt?", style={'textAlign': 'center'}),
                html.Div([
                    html.Div("stimme zu", style={'flex': '1', 'textAlign': 'center'}),
                    html.Div("stimme eher zu", style={'flex': '1', 'textAlign': 'center'}),
                    html.Div("neutral", style={'flex': '1', 'textAlign': 'center'}),
                    html.Div("stimme eher nicht zu", style={'flex': '1', 'textAlign': 'center'}),
                    html.Div("stimme nicht zu", style={'flex': '1', 'textAlign': 'center'})
                ], style={'display': 'flex', 'width': '80%', 'margin': '10px auto'}),
                html.Div("Hier kommen die Checkboxen hin", style={'margin': '20px 0'})
            ], style={
                "position": "absolute",
                "top": "10%",
                "left": "10%",
                "width": "80%",
                "height": "80%"
            })
        ]
    elif page_num == 103:
        umfrage_elemente = [
            html.Div([
                html.H1("1. Wissenstest", style={'textAlign': 'center'}),
                html.H2("Frage: Wie zufrieden sind Sie insgesamt mit dem Produkt?", style={'textAlign': 'center'}),
                html.Div([
                    html.Div("sehr zufrieden", style={'flex': '1', 'textAlign': 'center'}),
                    html.Div("zufrieden", style={'flex': '1', 'textAlign': 'center'}),
                    html.Div("neutral", style={'flex': '1', 'textAlign': 'center'}),
                    html.Div("unzufrieden", style={'flex': '1', 'textAlign': 'center'}),
                    html.Div("sehr unzufrieden", style={'flex': '1', 'textAlign': 'center'})
                ], style={'display': 'flex', 'width': '80%', 'margin': '10px auto'}),
                html.Div("Hier kommen die Checkboxen hin", style={'margin': '20px 0'})
            ], style={
                "position": "absolute",
                "top": "10%",
                "left": "10%",
                "width": "80%",
                "height": "80%"
            })
        ]
    elif page_num == 104:
        umfrage_elemente = [
            html.Div([
                html.H1("1. Wissenstest", style={'textAlign': 'center'}),
                html.H2("Frage: Was wuerde Sie dazu bringen, das Produkt haeufiger zu nutzen?", style={'textAlign': 'center'}),
                html.Div("Hier kommt das Textfeld hin", style={'margin': '20px 0', 'height': '100px', 'border': '1px solid black'})
            ], style={
                "position": "absolute",
                "top": "10%",
                "left": "10%",
                "width": "80%",
                "height": "80%"
            })
        ]
    elif page_num == 105:
        umfrage_elemente = [
            html.Div([
                html.H1("1. Wissenstest", style={'textAlign': 'center'}),
                html.H2("Frage: Was wuerde Sie dazu bringen, das Produkt haeufiger zu nutzen?", style={'textAlign': 'center'}),
                html.Div("Hier kommt das Textfeld hin", style={'margin': '20px 0', 'height': '100px', 'border': '1px solid black'})
            ], style={
                "position": "absolute",
                "top": "10%",
                "left": "10%",
                "width": "80%",
                "height": "80%"
            })
        ]
    elif page_num == 106:
        umfrage_elemente = [
            html.Div([
                html.H1("1. Wissenstest", style={'textAlign': 'center'}),
                html.H2("Frage: Was wuerde Sie dazu bringen, das Produkt haeufiger zu nutzen?", style={'textAlign': 'center'}),
                html.Div("Hier kommt das Textfeld hin", style={'margin': '20px 0', 'height': '100px', 'border': '1px solid black'})
            ], style={
                "position": "absolute",
                "top": "10%",
                "left": "10%",
                "width": "80%",
                "height": "80%"
            })
        ]
    elif page_num == 107:
        umfrage_elemente = [
            html.Div([
                html.H1("1. Wissenstest", style={'textAlign': 'center'}),
                html.H2("Frage: Was wuerde Sie dazu bringen, das Produkt haeufiger zu nutzen?", style={'textAlign': 'center'}),
                html.Div("Hier kommt das Textfeld hin", style={'margin': '20px 0', 'height': '100px', 'border': '1px solid black'})
            ], style={
                "position": "absolute",
                "top": "10%",
                "left": "10%",
                "width": "80%",
                "height": "80%"
            })
        ]
    elif page_num == 108:
        umfrage_elemente = [
            html.Div([
                html.H1("1. Wissenstest", style={'textAlign': 'center'}),
                html.H2("Frage: Was wuerde Sie dazu bringen, das Produkt haeufiger zu nutzen?", style={'textAlign': 'center'}),
                html.Div("Hier kommt das Textfeld hin", style={'margin': '20px 0', 'height': '100px', 'border': '1px solid black'})
            ], style={
                "position": "absolute",
                "top": "10%",
                "left": "10%",
                "width": "80%",
                "height": "80%"
            })
        ]
    elif page_num == 109:
        umfrage_elemente = [
            html.Div([
                html.H1("1. Wissenstest", style={'textAlign': 'center'}),
                html.H2("Frage: Was wuerde Sie dazu bringen, das Produkt haeufiger zu nutzen?", style={'textAlign': 'center'}),
                html.Div("Hier kommt das Textfeld hin", style={'margin': '20px 0', 'height': '100px', 'border': '1px solid black'})
            ], style={
                "position": "absolute",
                "top": "10%",
                "left": "10%",
                "width": "80%",
                "height": "80%"
            })
        ]
    elif page_num == 110:
        umfrage_elemente = [
            html.Div([
                html.H1("1. Wissenstest", style={'textAlign': 'center'}),
                html.H2("Frage: Was wuerde Sie dazu bringen, das Produkt haeufiger zu nutzen?", style={'textAlign': 'center'}),
                html.Div("Hier kommt das Textfeld hin", style={'margin': '20px 0', 'height': '100px', 'border': '1px solid black'})
            ], style={
                "position": "absolute",
                "top": "10%",
                "left": "10%",
                "width": "80%",
                "height": "80%"
            })
        ]


    #print("!!!!!HALLOOOOOO")
    text_fields = []
    if page_num in TEXT_FIELDS:
        for field in TEXT_FIELDS[page_num]:
            text_fields.append(
                html.Div(
                    dcc.Textarea(
                        id={'type': 'text-field', 'index': field["id"]},
                        value=TEXT_FIELD_VALUES[page_num][field["id"]] if TEXT_FIELD_VALUES[page_num][field["id"]] != None else "",  #zu Debug-Zwecken auf Hallo statt auf "" gesetzt
                        placeholder="",
                        style={
                            'width': f"{field['width']}%",  
                            'height': f"{field['height']}%",  
                            'padding': '10px',
                            'fontSize': '16px',
                            'border': '1px solid #ccc',
                            'borderRadius': '5px',
                            'backgroundColor': 'rgba(255, 255, 255, 0.8)',
                            'resize': 'none',  
                            #'pointerEvents': 'auto', 
                            'pointerEvents': 'none' if not field["changable"] else 'auto', # Interaktion erlauben
                            'opacity': '0.7' if not field["changable"] else '1' #
                            
                        }
                    ),
                    style={
                        "position": "absolute",
                        "top": f"{field['y']}%",  
                        "left": f"{field['x']}%",  
                        "width": f"{field['width']}%",  
                        "height": f"{field['height']}%",  
                        "transform": "translate(-50%, -50%)", 
                    }
                )
            )
    #Custom Textfelder: Die Textfelder von Seite 49 und 51 nochmal auf Seite 52 bis 57 einblenden
    if page_num == 52:
        field = TEXT_FIELDS[49][0] #Achtung Gefahr: Falls vor Textfeld 49-1 ein anderes eingefuegt wird, geht der Code nicht mehr
        text_fields.append(
                html.Div(
                    dcc.Textarea(
                        id={'type': 'text-field', 'index': field["id"]},
                        value=TEXT_FIELD_VALUES[49]["text-49-1"] if TEXT_FIELD_VALUES[49]["text-49-1"] != None else "",  
                        placeholder="",
                        style={
                            'width': f"{field['width']}%",  
                            'height': f"{field['height']}%",  
                            'padding': '10px',
                            'fontSize': '16px',
                            'border': '1px solid #ccc',
                            'borderRadius': '5px',
                            'backgroundColor': 'rgba(255, 255, 255, 0.8)',
                            'resize': 'none',  
                            #'pointerEvents': 'auto', 
                            'pointerEvents': 'none',
                            'opacity': '0.7' #
                            
                        }
                    ),
                    style={
                        "position": "absolute",
                        "top": f"20%", #hier custom Wert wurde eingetragen  
                        "left": f"{field['x']}%",  
                        "width": f"{field['width']}%",  
                        "height": f"{field['height']}%",  
                        "transform": "translate(-50%, -50%)", 
                    }
                )
            )

    if page_num == 53:
        field = TEXT_FIELDS[49][0] #Achtung Gefahr: Falls vor Textfeld 49-1 ein anderes eingefuegt wird, geht der Code nicht mehr
        text_fields.append(
                html.Div(
                    dcc.Textarea(
                        id={'type': 'text-field', 'index': field["id"]},
                        value=TEXT_FIELD_VALUES[49]["text-49-1"] if TEXT_FIELD_VALUES[49]["text-49-1"] != None else "",  
                        placeholder="",
                        style={
                            'width': f"{field['width']}%",  
                            'height': f"{field['height']}%",  
                            'padding': '10px',
                            'fontSize': '16px',
                            'border': '1px solid #ccc',
                            'borderRadius': '5px',
                            'backgroundColor': 'rgba(255, 255, 255, 0.8)',
                            'resize': 'none',  
                            #'pointerEvents': 'auto', 
                            'pointerEvents': 'none',
                            'opacity': '0.7' #
                            
                        }
                    ),
                    style={
                        "position": "absolute",
                        "top": f"20%",  #hier custom Wert wurde eingetragen 
                        "left": f"{field['x']}%",  
                        "width": f"{field['width']}%",  
                        "height": f"{field['height']}%",  
                        "transform": "translate(-50%, -50%)", 
                    }
                )
            )

    if page_num == 54:
        field = TEXT_FIELDS[49][1] #Achtung Gefahr: Falls vor Textfeld 49-2 ein anderes eingefuegt wird, geht der Code nicht mehr
        text_fields.append(
                html.Div(
                    dcc.Textarea(
                        id={'type': 'text-field', 'index': field["id"]},
                        value=TEXT_FIELD_VALUES[49]["text-49-2"] if TEXT_FIELD_VALUES[49]["text-49-2"] != None else "",  
                        placeholder="",
                        style={
                            'width': f"{field['width']}%",  
                            'height': f"{field['height']}%",  
                            'padding': '10px',
                            'fontSize': '16px',
                            'border': '1px solid #ccc',
                            'borderRadius': '5px',
                            'backgroundColor': 'rgba(255, 255, 255, 0.8)',
                            'resize': 'none',  
                            #'pointerEvents': 'auto', 
                            'pointerEvents': 'none',
                            'opacity': '0.7' #
                            
                        }
                    ),
                    style={
                        "position": "absolute",
                        "top": f"20%",  #hier custom Wert wurde eingetragen 
                        "left": f"{field['x']}%",  
                        "width": f"{field['width']}%",  
                        "height": f"{field['height']}%",  
                        "transform": "translate(-50%, -50%)", 
                    }
                )
            )

    if page_num == 55:
        field = TEXT_FIELDS[50][0] #Achtung Gefahr: Falls vor Textfeld 49-2 ein anderes eingefuegt wird, geht der Code nicht mehr
        text_fields.append(
                html.Div(
                    dcc.Textarea(
                        id={'type': 'text-field', 'index': field["id"]},
                        value=TEXT_FIELD_VALUES[50]["text-50-1"] if TEXT_FIELD_VALUES[50]["text-50-1"] != None else "",  
                        placeholder="",
                        style={
                            'width': f"{field['width']}%",  
                            'height': f"{field['height']}%",  
                            'padding': '10px',
                            'fontSize': '16px',
                            'border': '1px solid #ccc',
                            'borderRadius': '5px',
                            'backgroundColor': 'rgba(255, 255, 255, 0.8)',
                            'resize': 'none',  
                            #'pointerEvents': 'auto', 
                            'pointerEvents': 'none',
                            'opacity': '0.7' #
                            
                        }
                    ),
                    style={
                        "position": "absolute",
                        "top": f"20%",  #hier custom Wert wurde eingetragen 
                        "left": f"{field['x']}%",  
                        "width": f"{field['width']}%",  
                        "height": f"{field['height']}%",  
                        "transform": "translate(-50%, -50%)", 
                    }
                )
            )
    
    if page_num == 56:
        field = TEXT_FIELDS[50][1] #Achtung Gefahr: Falls vor Textfeld 49-2 ein anderes eingefuegt wird, geht der Code nicht mehr
        text_fields.append(
                html.Div(
                    dcc.Textarea(
                        id={'type': 'text-field', 'index': field["id"]},
                        value=TEXT_FIELD_VALUES[50]["text-50-2"] if TEXT_FIELD_VALUES[50]["text-50-2"] != None else "",  
                        placeholder="",
                        style={
                            'width': f"{field['width']}%",  
                            'height': f"{field['height']}%",  
                            'padding': '10px',
                            'fontSize': '16px',
                            'border': '1px solid #ccc',
                            'borderRadius': '5px',
                            'backgroundColor': 'rgba(255, 255, 255, 0.8)',
                            'resize': 'none',  
                            #'pointerEvents': 'auto', 
                            'pointerEvents': 'none',
                            'opacity': '0.7' #
                            
                        }
                    ),
                    style={
                        "position": "absolute",
                        "top": f"20%",  #hier custom Wert wurde eingetragen 
                        "left": f"{field['x']}%",  
                        "width": f"{field['width']}%",  
                        "height": f"{field['height']}%",  
                        "transform": "translate(-50%, -50%)", 
                    }
                )
            )

    if page_num == 57:
        field = TEXT_FIELDS[51][0] #Achtung Gefahr: Falls vor Textfeld 49-2 ein anderes eingefuegt wird, geht der Code nicht mehr
        text_fields.append(
                html.Div(
                    dcc.Textarea(
                        id={'type': 'text-field', 'index': field["id"]},
                        value=TEXT_FIELD_VALUES[51]["text-51-1"] if TEXT_FIELD_VALUES[51]["text-51-1"] != None else "",  
                        placeholder="",
                        style={
                            'width': f"{field['width']}%",  
                            'height': f"{field['height']}%",  
                            'padding': '10px',
                            'fontSize': '16px',
                            'border': '1px solid #ccc',
                            'borderRadius': '5px',
                            'backgroundColor': 'rgba(255, 255, 255, 0.8)',
                            'resize': 'none',  
                            #'pointerEvents': 'auto', 
                            'pointerEvents': 'none',
                            'opacity': '0.7' #
                            
                        }
                    ),
                    style={
                        "position": "absolute",
                        "top": f"20%", #hier custom Wert wurde eingetragen  
                        "left": f"{field['x']}%",  
                        "width": f"{field['width']}%",  
                        "height": f"{field['height']}%",  
                        "transform": "translate(-50%, -50%)", 
                    }
                )
            )
    
    # Automatisch alle Checkboxen generieren, die in CHECK_BOXES definiert sind
    check_boxes = []
    if page_num in CHECK_BOXES:
        for box in CHECK_BOXES[page_num]:
            check_boxes.append(
                html.Div(
                    dcc.Checklist(
                        id={'type': 'checkbox', 'index': box["id"]},#id=box["id"],
                        options=[{'label': '', 'value': 'checked'}],
                        value=['checked'] if CHECK_BOX_VALUES[page_num][box["id"]] == True else [],#box["checked"] else [],
                        style={
                            'pointerEvents': 'none' if not box["changable"] else 'auto', #'auto'  # Interaktion erlauben
                            'opacity': '0.5' if not box["changable"] else '1'
                        },
                        inputStyle={
                            'transform': f'scale({box["scale"]})',  # Skalierung
                            'transformOrigin': 'top left',
                            'margin': '10px'
                        }
                    ),
                    style={
                        "position": "absolute",
                        "top": f"{box['y']}%",  # Abstand von oben in Prozent
                        "left": f"{box['x']}%",  # Abstand von links in Prozent
                        "transform": "translate(-50%, -50%)"  # Zentriert die Checkbox
                    }
                )
            )
    
    
    buttons = []
    if page_num in BUTTONS:
        for button in BUTTONS[page_num]:
            buttons.append(
                html.Div(
                    html.Button(
                        button["label"], 
                        id={'type': 'dynamic-button', 'index': button["id"]},  # Hier dynamische ID!
                        n_clicks=0,
                        style={
                            'backgroundColor': button.get("background_color"),#'grey',
                            'color': 'black',
                            'border': 'none',
                            'padding': '10px 20px',
                            'fontSize': '16px',
                            'borderRadius': '5px',
                            'cursor': 'pointer'
                        }
                    ),
                    style={
                        "position": "absolute",
                        "top": f"{button['y']}%",  
                        "left": f"{button['x']}%",  
                        "transform": "translate(-50%, -50%)"  
                    }
                )
            )

    #hier in dem return statement wird das Div seitenuebergreifend einheitlich gestaltet und zurueckgegeben: text_fields + check_boxes + buttons
    return html.Div([
        html.Div(
            style={'position': 'relative', 'width': '80%', 'margin': '0 auto'},
            children=[
                html.Div(
                    style={
                        "position": "relative",
                        "width": "100%",  
                        "height": "auto",
                        "overflow": "hidden",
                    },
                    children=[
                        html.Img(
                            src=f"/assets/{files[page_num - 1]}",
                            style={
                                'width': '100%',
                                'height': 'auto',
                                'display': 'block',
                                'margin': '0 auto'
                            }
                        ),
                        html.Div(
                            style={
                                "position": "absolute",
                                "top": "0px",
                                "left": "0px",
                                "width": "100%",
                                "height": "100%",
                                "pointerEvents": "auto",
                            },
                            children=collapse_elemente + umfrage_elemente + text_fields + check_boxes + buttons + navigation_buttons + modal_button_elemente #+ umfrage_elemente #+ ([audio_div] if audio_div else [])
                        )#_VERBESSERUNG
                    ]
                )
            ]
        )
    ])

#####Dash: Callback-Funktionen mit denen der Nutzer mit der Dash-App interagieren kann: Buttons klicken, Seiten-Springen, usw.
#Dash-Callback: Jeweilige Seite anzeigen, auf der wir uns befinden
@app.callback(
    [Output('page-content', 'children'),
     Output('back-button', 'href'),
     Output('forward-button', 'href')],
    [Input('url', 'pathname')]
)
def display_page(pathname):
    if not pathname or pathname == "/":
        page_num = 1
    else:
        try:
            page_num = int(pathname.split('/')[-1])
        except ValueError:
            page_num = 1
    page_num = max(1, min(MAX_PAGES, page_num))

    back_href = f'/{page_num - 1}' if page_num > 1 else '/1'
    forward_href = f'/{page_num + 1}' if page_num < MAX_PAGES else f'/{MAX_PAGES}'

    return [create_page(page_num), back_href, forward_href]

#Dash-Callback: Springen zwischen den Seiten via Jump-Button oder der Navigationsleiste
@app.callback(
    Output('url', 'pathname'),
    [Input('jump-button', 'n_clicks'),
     Input('chapter-button', 'n_clicks')],
    [State('page-input', 'value'),
     State('chapter-input', 'value')]
)
def jump_to_page_or_chapter(jump_clicks, chapter_clicks, page_num, chapter_num):
    ctx = callback_context
    if not ctx.triggered:
        return no_update

    button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    global SESSION_ID_VALUE #_LOGGING
    if button_id == 'jump-button' and page_num:
        #_LOGGING
        log_interaction(user_id=SESSION_ID_VALUE, element_id = "JUMP_TO_PAGE", value = f"Nutzer ist zu Seite {page_num}")
        return f'/{max(1, min(MAX_PAGES, page_num))}'
    elif button_id == 'chapter-button' and chapter_num in CHAPTER_MAPPING:
        #_LOGGING
        log_interaction(user_id=SESSION_ID_VALUE, element_id = "JUMP_TO_CHAPTER", value = f"Nutzer ist zu Kapitel {chapter_num}")
        return f'/{CHAPTER_MAPPING[chapter_num]}'
    return no_update

#Update des Login-Status
@app.callback(
    Output('login-status', 'children'),
    Input('update-interval', 'n_intervals')
)
def update_login_status(n):
    global SESSION_ID_VALUE
    if SESSION_ID_VALUE != None:
        #log_interaction(user_id=SESSION_ID_VALUE, element_id = "Login-Status", value = "Nutzer hat sich eingeloggt.")
        return f"Eingeloggt mit Kennung: {SESSION_ID_VALUE}"
    else:
        return "Nicht eingeloggt!"

#Dash Callback: Fuer alle weiteren Buttons ausserhalb der Navigationsleiste (bedienen sich an der globalen Datenstruktur Buttons)
@app.callback(
    Output('dummy-output', 'children'),
    Input({'type': 'dynamic-button', 'index': dash.ALL}, 'n_clicks'),
    prevent_initial_call=True
)
def button_callback(n_clicks):
    ctx = callback_context

    if not ctx.triggered:
        raise PreventUpdate  # Kein Button wurde geklickt

    # Finde heraus, welcher Button geklickt wurde
    triggered_button = ctx.triggered[0]['prop_id'].split('.')[0]
    button_id = eval(triggered_button)  # {'type': 'dynamic-button', 'index': XYZ}

    # Falls n_clicks None oder 0 ist, soll nichts passieren
    if not any(n_clicks):  
        raise PreventUpdate  

    print(f"Button {button_id['index']} wurde geklickt!")  # Debug-Output

    # Suche den geklickten Button in der BUTTONS-Datenstruktur
    for page, buttons in BUTTONS.items():
        for button in buttons:
            if button["id"] == button_id['index']:
                #_LOGGING
                global SESSION_ID_VALUE
                button_id_extrahiert = button["id"]
                log_interaction(user_id=SESSION_ID_VALUE, element_id = "Button-Inpage-Klick", value = f"Button mit ID {button_id_extrahiert} auf Seite {page} wurde geklickt.")
                method = button["method"]
                if callable(method):
                    print(f"Starte Methode {method.__name__}...")
                    threading.Thread(target=method).start()  # Starte Methode in eigenem Thread
                return no_update

    return no_update

#Textfelder: Automatisches Updaten mithilfe von json-requests an /save_text_field; Zieht sich alle Textfelder, die die Struktur {'type': 'text-field', 'index'} haben
@app.callback(
    Output('dummy-output2', 'style'),
    Input('update-interval', 'n_intervals'),
    Input({'type': 'text-field', 'index': dash.ALL}, 'id'),
    Input({'type': 'text-field', 'index': dash.ALL}, 'value'),
    prevent_initial_call=True
)
def autosave_texts(n_intervals, ids, values):
    print("!!!!!!!!!!AUTOSAVE TEXTS WIRD AUFGERUFEN.")
    
    current_ids = [dictionary['index'] for dictionary in ids]
    value_dict = dict(zip(current_ids, values))
    
    print("autosave_texts: IDs und Values: ", value_dict)

    try:
        # Senden der Daten an die Flask-Route
        save_text_fields_link = f"{host_ip}:{flask_port}/save_text_fields"   #HIER WURDE DIE IP ADRESSE UEBERAREITET'http://127.0.0.1:5000/save_text_fields'
        response = requests.post(save_text_fields_link, 
                                 json={'dict_ids_values': value_dict})
        if response.status_code == 200:
            print("Alle Textfelder erfolgreich gespeichert")
        else:
            print(f"Fehler beim Speichern der Textfelder: {response.text}")
    except Exception as e:
        print(f"Fehler bei der Uebertragung: {str(e)}")

    return {'display': 'none'}


@app.callback(
    Output('dummy-output', 'style'),
    Input('update-interval', 'n_intervals'),
    Input({'type': 'checkbox', 'index': dash.ALL}, 'id'),
    Input({'type': 'checkbox', 'index': dash.ALL}, 'value'),
    prevent_initial_call=True
)
def autosave_checkboxes(n_intervals, ids, values):
    print("!!!!!!!!!!AUTOSAVE CHECKBOXES WIRD AUFGERUFEN.")
    current_ids = [dictionary['index'] for dictionary in ids]
    #values_boolformat = [('checked' in x) for x in values]  #Umwandeln [['checked'], [''], ...] in [True, False, ...]
    print("autosave_checkboxes: values: ", values)#, " value_bools: ", values_boolformat)
    value_dict = dict(zip(current_ids, values))#_boolformat))
    
    print("Checkbox IDs und Values: ", value_dict)

    try:
        # Senden der Daten an die Flask-Route
        save_checkboxes_link = f"{host_ip}:{flask_port}/save_checkboxes" #IP ADRESSE WURDE HIER UEBERARBEITET'http://127.0.0.1:5000/save_checkboxes'
        response = requests.post(save_checkboxes_link, 
                                 json={'dict_ids_values': value_dict})
        if response.status_code == 200:
            print("Alle Checkboxen erfolgreich gespeichert")
        else:
            print(f"Fehler beim Speichern der Checkboxen: {response.text}")
    except Exception as e:
        print(f"Fehler bei der Uebertragung: {str(e)}")

    return {'display': 'none'}

#####Socket-Callbacks
@socketio_dashclient.on('textfields_to_dash')
def handle_textfield_change(data=None):
    global TEXT_FIELD_VALUES
    print("handle_textfield_change: Erhaltene Textfelder: ", data)
    if data == None:
        return
    for page_str in data:
        print("handle_textfield_change: page_str: ", page_str)
        for text_field_id in data[page_str]:
            #_LOGGING
            global SESSION_ID_VALUE
            old_value = TEXT_FIELD_VALUES[int(page_str)][text_field_id]
            new_value = data[page_str][text_field_id]
            if old_value != new_value:
                log_interaction(user_id=SESSION_ID_VALUE, element_id = "Textfield-Update", value = f"Textfeld auf Seite {page_str} mit Textfield-ID {text_field_id}. Alter Wert: {old_value}. Neuer Wert: {new_value}")
            TEXT_FIELD_VALUES[int(page_str)][text_field_id] = data[page_str][text_field_id]
    print("handle_textfield_change: TEXT_FIELD_VALUES: ", TEXT_FIELD_VALUES)
        
@socketio_dashclient.on('checkboxes_to_dash')
def handle_checkboxes_change(data=None):
    global CHECK_BOX_VALUES
    if data == None:
        return
    print("handle_checkboxes_change: Erhaltene Checkboxen: ", data)
    for page_str in data:
        print("handle_checkbox_change: page_str: ", page_str)
        for checkbox_id in data[page_str]:
            #_LOGGING
            global SESSION_ID_VALUE
            old_value = CHECK_BOX_VALUES[int(page_str)][checkbox_id]
            new_value = data[page_str][checkbox_id]
            if old_value != new_value:
                log_interaction(user_id=SESSION_ID_VALUE, element_id = "Checkbox-Update", value = f"Checkbox auf Seite {page_str} mit Checkbox-ID {checkbox_id}. Alter Wert: {old_value}. Neuer Wert: {new_value}")
            CHECK_BOX_VALUES[int(page_str)][checkbox_id] = data[page_str][checkbox_id]
    print("handle_checkboxes_change: CHECK_BOXES_VALUES: ", CHECK_BOX_VALUES)

@socketio_dashclient.on('session_id_to_dash')
def handle_session_id_change(data):
    global SESSION_ID_VALUE
    print("handle_session_id_change: Erhaltene Session_ID: ", data)
    #if data == None:
    #    return
    SESSION_ID_VALUE = data
    print("handle_session_id_change: TEXT_FIELD_VALUES: ", SESSION_ID_VALUE)


######### Modal Callbacks
@app.callback(
    Output("zeichenfenster-modal", "is_open"),
    [Input("open-zeichenfenster-modal", "n_clicks"), Input("close-modal", "n_clicks")],
    [State("zeichenfenster-modal", "is_open")],
)
def toggle_zeichenfenster_modal(n1, n2, is_open):
    if n1 or n2:
        global SESSION_ID_VALUE #_LOGGING
        if n1:
            #_LOGGING
            log_interaction(user_id=SESSION_ID_VALUE, element_id = "Zeichenfenster-Oeffnung", value = "Zeichenfenster wurde geoeffnet.")
        if n2:
            #_LOGGING
            log_interaction(user_id=SESSION_ID_VALUE, element_id = "Zeichenfenster-Schliessung", value = "Zeichenfenster wurde geschlossen.")
        return not is_open
    return is_open

@app.callback(
    Output("zeichenfenster-modal-ohne-ks", "is_open"),
    [Input("open-zeichenfenster-modal-ohne-ks", "n_clicks"), Input("close-modal", "n_clicks")],
    [State("zeichenfenster-modal-ohne-ks", "is_open")],
)
def toggle_zeichenfenster_modal_ohne_ks(n1, n2, is_open):
    if n1 or n2:
        global SESSION_ID_VALUE
        if n1:
            #_LOGGING
            log_interaction(user_id=SESSION_ID_VALUE, element_id = "Zeichenfenster-ohne-KS-Oeffnung", value = "Zeichenfenster ohne Koordinatensystem wurde geoeffnet.")
        if n2:
            #_LOGGING
            log_interaction(user_id=SESSION_ID_VALUE, element_id = "Zeichenfenster-ohne-KS-Schliessung", value = "Zeichenfenster ohne Koordinatensystem wurde geschlossen.")
        return not is_open
    return is_open

@app.callback(
    Output("audioaufnahme-modal", "is_open"),
    [Input("open-audioaufnahme-modal", "n_clicks"), Input("close-modal", "n_clicks")],
    [State("audioaufnahme-modal", "is_open")],
)
def toggle_audioaufnahme(n1, n2, is_open):
    if n1 or n2:
        global SESSION_ID_VALUE
        if n1:
            #_LOGGING
            log_interaction(user_id=SESSION_ID_VALUE, element_id = "Audiofenster-Oeffnung", value = "Audiofenster wurde geoeffnet.")
        if n2:
            #_LOGGING
            log_interaction(user_id=SESSION_ID_VALUE, element_id = "Audiofenster-Schliessung", value = "Audiofenster wurde geschlossen.")
        return not is_open
    return is_open


@app.callback(
    Output("yt-kommentaranalyse-modal", "is_open"),
    [Input("open-yt-kommentaranalyse-modal", "n_clicks"), Input("close-modal", "n_clicks")],
    [State("yt-kommentaranalyse-modal", "is_open")],
)
def toggle_yt_kommentaranalse(n1, n2, is_open):
    if n1 or n2:
        global SESSION_ID_VALUE
        if n1:
            #_LOGGING
            log_interaction(user_id=SESSION_ID_VALUE, element_id = "YT-Kommentaranalyse-Fenster-Oeffnung", value = "YT-Kommentaranalyse-Fenster wurde geoeffnet.")
        if n2:
            #_LOGGING
            log_interaction(user_id=SESSION_ID_VALUE, element_id = "YT-Kommentaranalyse-Fenster-Schliessung", value = "YT-Kommentaranalyse-Fenster wurde geschlossen.")
        return not is_open
    return is_open


@app.callback(
    Output("kameraanalyse-modal", "is_open"),
    [Input("open-kameraanalyse-modal", "n_clicks"), Input("close-modal", "n_clicks")],
    [State("kameraanalyse-modal", "is_open")],
)
def toggle_kameraanalyse(n1, n2, is_open):
    if n1 or n2:
        global SESSION_ID_VALUE
        if n1:
            #_LOGGING
            log_interaction(user_id=SESSION_ID_VALUE, element_id = "Kameraanalyse-Fenster-Oeffnung", value = "Kameraanalyse-Fenster wurde geoeffnet.")
        if n2:
            #_LOGGING
            log_interaction(user_id=SESSION_ID_VALUE, element_id = "Kameraanalyse-Fenster-Schliessung", value = "Kameraanalyse-Fenster wurde geschlossen.")
        return not is_open
    return is_open

for i in range(1, 9): #_Verbesserung
    @app.callback(
        Output(f"collapse-{i}", "is_open"),
        [Input(f"collapse-button-{i}", "n_clicks")],
        [State(f"collapse-{i}", "is_open")],
    )
    def toggle_collapse(n, is_open, i=i):
        global SESSION_ID_VALUE
        if n:
            if not is_open:  # Collapse wird geoeffnet
                log_interaction(user_id=SESSION_ID_VALUE, element_id=f"Collapse-Button-{i}-Oeffnung", value=f"Collapse {i} wurde geoeffnet.")
            elif is_open:  # Collapse wird geschlossen
                log_interaction(user_id=SESSION_ID_VALUE, element_id=f"Collapse-Button-{i}-Schliessung", value=f"Collapse {i} wurde geschlossen.")
            return not is_open
        return is_open
'''
@app.callback(
    Output('audio-data-output', 'children'),
    Input('audio-data-store', 'data')
)
def update_audio_output(audio_data):
    if audio_data:
        # Hier koennen Sie die Audiodaten verarbeiten
        # Beispiel: Zeige die letzten 5 Werte an
        last_values = audio_data[-5:]
        return f"Letzte 5 Audiowerte: {last_values}"
    return "Keine Audiodaten verfuegbar"
'''
'''
app.clientside_callback(
    """
    function(n_intervals) {
        var audioData = [];
        
        function receiveMessage(event) {
            if (event.data.type === 'audioData') {
                audioData = event.data.data;
            }
        }
        
        window.addEventListener('message', receiveMessage, false);
        
        return audioData;
    }
    """,
    Output('audio-data-store', 'data'),
    Input('audio-data-interval', 'n_intervals')
)'''





##########Flask App Ausfuehrung und Dash App Ausfuehrung
#####Startet Dash (im Main-Thread)
def run_dash():
    print("Dash wird gestartet.")
    app.run_server(debug=True, host='0.0.0.0', port=8050)
    print("Dash wurde gestartet.")
    #socketio_dashclient.connect(f"http://{host_ip}:{flask_port}")
    #print("Dash: Der Socket vom Flask aus wurde gestartet.")

if __name__ == '__main__':
    print("Dash: Der Socket vom Flask aus wurde gestartet.")
    run_dash()
    #socketio_dashclient.connect(f"{host_ip}:{flask_port}")





'''
umfrage_elemente = []
    if page_num == 100:
        umfrage_elemente = [
            html.Div([
                html.H1("1. Wissenstest", style={'textAlign': 'center'}),
                html.H2("Frage 1: Wissenspruefung 1"),
                html.Div([
                    html.Div("stimme zu", style={'flex': '1', 'textAlign': 'center'}),
                    html.Div("stimme eher zu", style={'flex': '1', 'textAlign': 'center'}),
                    html.Div("neutral", style={'flex': '1', 'textAlign': 'center'}),
                    html.Div("stimme eher nicht zu", style={'flex': '1', 'textAlign': 'center'}),
                    html.Div("stimme nicht zu", style={'flex': '1', 'textAlign': 'center'})
                ], style={'display': 'flex', 'width': '80%', 'margin': '10px auto'}),
                html.Div("Hier kommen die Checkboxen hin", style={'margin': '20px 0'}),
                html.H2("Frage 2: Wissenspruefung 2."),
                html.Div("Hier kommt das Textfeld hin", style={'margin': '20px 0', 'height': '100px', 'border': '1px solid black'})
            ], style={
                "position": "absolute",
                "top": "10%",
                "left": "10%",
                "width": "80%",
                "height": "80%"
            })
        ]
    elif page_num == 101:
        umfrage_elemente = [
            html.H1("1. Wissenstest", style={'textAlign': 'center', 'marginTop': '150px'}),
            html.H2("Frage 1: Hier Frage"),
            html.Div("Hier kommt das Textfeld hin", style={'margin': '20px 0', 'height': '100px', 'border': '1px solid black'}),
            html.H2("Frage 2: Hier Frage"),
            html.Div("Hier kommt das Textfeld hin", style={'margin': '20px 0', 'height': '100px', 'border': '1px solid black'}),
            html.H2("Frage 2: Hier Frage"),
            html.Div("Hier kommt das Textfeld hin", style={'margin': '20px 0', 'height': '100px', 'border': '1px solid black'}),
            html.H2("Frage 2: Hier Frage"),
            html.Div("Hier kommt das Textfeld hin", style={'margin': '20px 0', 'height': '100px', 'border': '1px solid black'}),
            html.H2("Frage 2: Hier Frage"),
            html.Div("Hier kommt das Textfeld hin", style={'margin': '20px 0', 'height': '100px', 'border': '1px solid black'}),

        ]
    elif page_num == 102:
        umfrage_elemente = [
            html.H1("1. Wissenstest", style={'textAlign': 'center', 'marginTop': '150px'}),
            html.H2("Frage: Wie oft nutzen Sie das Produkt?"),
            html.Div(["taeglich", "mehrmals pro Woche", "einmal pro Woche", "seltener", "nie"], style={'display': 'flex', 'justifyContent': 'space-between', 'width': '80%', 'margin': '10px auto'}),
            html.Div("Hier kommen die Checkboxen hin", style={'margin': '20px 0'})
        ]
    elif page_num == 103:
        umfrage_elemente = [
            html.H1("1. Wissenstest", style={'textAlign': 'center', 'marginTop': '150px'}),
            html.H2("Frage: Wie zufrieden sind Sie insgesamt mit dem Produkt?"),
            html.Div(["sehr zufrieden", "zufrieden", "neutral", "unzufrieden", "sehr unzufrieden"], style={'display': 'flex', 'justifyContent': 'space-between', 'width': '80%', 'margin': '10px auto'}),
            html.Div("Hier kommen die Checkboxen hin", style={'margin': '20px 0'})
        ]
    elif page_num == 104:
        umfrage_elemente = [
            html.H1("1. Wissenstest", style={'textAlign': 'center', 'marginTop': '150px'}),
            html.H2("Frage: Was wuerde Sie dazu bringen, das Produkt haeufiger zu nutzen?"),
            html.Div("Hier kommt das Textfeld hin", style={'margin': '20px 0', 'height': '100px', 'border': '1px solid black'})
        ]
    elif page_num == 105:
        umfrage_elemente = [
            html.H1("1. Wissenstest", style={'textAlign': 'center', 'marginTop': '150px'}),
            html.H2("Frage: Was wuerde Sie dazu bringen, das Produkt haeufiger zu nutzen?"),
            html.Div("Hier kommt das Textfeld hin", style={'margin': '20px 0', 'height': '100px', 'border': '1px solid black'})
        ]
    elif page_num == 106:
        umfrage_elemente = [
            html.H1("1. Wissenstest", style={'textAlign': 'center', 'marginTop': '150px'}),
            html.H2("Frage: Was wuerde Sie dazu bringen, das Produkt haeufiger zu nutzen?"),
            html.Div("Hier kommt das Textfeld hin", style={'margin': '20px 0', 'height': '100px', 'border': '1px solid black'})
        ]
    elif page_num == 107:
        umfrage_elemente = [
            html.H1("1. Wissenstest", style={'textAlign': 'center', 'marginTop': '150px'}),
            html.H2("Frage: Was wuerde Sie dazu bringen, das Produkt haeufiger zu nutzen?"),
            html.Div("Hier kommt das Textfeld hin", style={'margin': '20px 0', 'height': '100px', 'border': '1px solid black'})
        ]
    elif page_num == 108:
        umfrage_elemente = [
            html.H1("1. Wissenstest", style={'textAlign': 'center', 'marginTop': '150px'}),
            html.H2("Frage: Was wuerde Sie dazu bringen, das Produkt haeufiger zu nutzen?"),
            html.Div("Hier kommt das Textfeld hin", style={'margin': '20px 0', 'height': '100px', 'border': '1px solid black'})
        ]
    elif page_num == 109:
        umfrage_elemente = [
            html.H1("1. Wissenstest", style={'textAlign': 'center', 'marginTop': '150px'}),
            html.H2("Frage: Was wuerde Sie dazu bringen, das Produkt haeufiger zu nutzen?"),
            html.Div("Hier kommt das Textfeld hin", style={'margin': '20px 0', 'height': '100px', 'border': '1px solid black'})
        ]
    elif page_num == 110:
        umfrage_elemente = [
            html.H1("2. Gestaltung und Nutzerfreundlichkeit", style={'textAlign': 'center', 'marginTop': '150px'}),
            html.H2("Frage 1: Wie bewerten Sie das Design des Produkts?"),
            html.Div(["stimme zu", "stimme eher zu", "neutral", "stimme eher nicht zu", "stimme nicht zu"], style={'display': 'flex', 'justifyContent': 'space-between', 'width': '80%', 'margin': '10px auto'}),
            html.Div("Hier kommen die Checkboxen hin", style={'margin': '20px 0'}),
            html.H2("Frage 2: Was wuerden Sie am Design aendern?"),
            html.Div("Hier kommt das Textfeld hin", style={'margin': '20px 0', 'height': '100px', 'border': '1px solid black'})
        ]
    elif page_num == 111:
        umfrage_elemente = [
            html.H1("2. Gestaltung und Nutzerfreundlichkeit", style={'textAlign': 'center', 'marginTop': '150px'}),
            html.H2("Frage: Welche Funktion des Produkts nutzen Sie am haeufigsten?"),
            html.Div("Hier kommt das Textfeld hin", style={'margin': '20px 0', 'height': '100px', 'border': '1px solid black'})
        ]
    elif page_num == 112:
        umfrage_elemente = [
            html.H1("2. Gestaltung und Nutzerfreundlichkeit", style={'textAlign': 'center', 'marginTop': '150px'}),
            html.H2("Frage: Wie wahrscheinlich ist es, dass Sie das Produkt weiterempfehlen?"),
            html.Div(["sehr wahrscheinlich", "wahrscheinlich", "neutral", "unwahrscheinlich", "sehr unwahrscheinlich"], style={'display': 'flex', 'justifyContent': 'space-between', 'width': '80%', 'margin': '10px auto'}),
            html.Div("Hier kommen die Checkboxen hin", style={'margin': '20px 0'})
        ]
    elif page_num == 113:
        umfrage_elemente = [
            html.H1("2. Gestaltung und Nutzerfreundlichkeit", style={'textAlign': 'center', 'marginTop': '150px'}),
            html.H2("Frage: Wie wahrscheinlich ist es, dass Sie das Produkt weiterempfehlen?"),
            html.Div(["sehr wahrscheinlich", "wahrscheinlich", "neutral", "unwahrscheinlich", "sehr unwahrscheinlich"], style={'display': 'flex', 'justifyContent': 'space-between', 'width': '80%', 'margin': '10px auto'}),
            html.Div("Hier kommen die Checkboxen hin", style={'margin': '20px 0'})
        ]
    elif page_num == 114:
        umfrage_elemente = [
            html.H1("2. Gestaltung und Nutzerfreundlichkeit", style={'textAlign': 'center', 'marginTop': '150px'}),
            html.H2("Frage: Wie wahrscheinlich ist es, dass Sie das Produkt weiterempfehlen?"),
            html.Div(["sehr wahrscheinlich", "wahrscheinlich", "neutral", "unwahrscheinlich", "sehr unwahrscheinlich"], style={'display': 'flex', 'justifyContent': 'space-between', 'width': '80%', 'margin': '10px auto'}),
            html.Div("Hier kommen die Checkboxen hin", style={'margin': '20px 0'})
        ]
    elif page_num == 115:
        umfrage_elemente = [
            html.H1("2. Gestaltung und Nutzerfreundlichkeit", style={'textAlign': 'center', 'marginTop': '150px'}),
            html.H2("Frage: Wie wahrscheinlich ist es, dass Sie das Produkt weiterempfehlen?"),
            html.Div(["sehr wahrscheinlich", "wahrscheinlich", "neutral", "unwahrscheinlich", "sehr unwahrscheinlich"], style={'display': 'flex', 'justifyContent': 'space-between', 'width': '80%', 'margin': '10px auto'}),
            html.Div("Hier kommen die Checkboxen hin", style={'margin': '20px 0'})
        ]
    elif page_num == 116:
        umfrage_elemente = [
            html.H1("3. Analyse einzelner Elemente", style={'textAlign': 'center', 'marginTop': '150px'}),
            html.H2("Frage 1: Wie zufrieden sind Sie mit der Funktionalitaet des Produkts?"),
            html.Div(["stimme zu", "stimme eher zu", "neutral", "stimme eher nicht zu", "stimme nicht zu"], style={'display': 'flex', 'justifyContent': 'space-between', 'width': '80%', 'margin': '10px auto'}),
            html.Div("Hier kommen die Checkboxen hin", style={'margin': '20px 0'}),
            html.H2("Frage 2: Welche Funktionen wuerden Sie sich zusaetzlich wuenschen?"),
            html.Div("Hier kommt das Textfeld hin", style={'margin': '20px 0', 'height': '100px', 'border': '1px solid black'})
        ]
    elif page_num == 117:
        umfrage_elemente = [
            html.H1("Abschliessende Gedanken", style={'textAlign': 'center', 'marginTop': '150px'}),
            html.H2("Frage: Haben Sie noch weitere Anmerkungen oder Vorschlaege zur Verbesserung des Produkts?"),
            html.Div("Hier kommt das Textfeld hin", style={'margin': '20px 0', 'height': '100px', 'border': '1px solid black'})
        ]
    elif page_num == 118:
        umfrage_elemente = [
            html.H1("Umfrage - Seite 110", style={'textAlign': 'center', 'marginTop': '150px'}),
            html.H2("Abschluss"),
            html.P("Vielen Dank fuer Ihre Teilnahme an der Umfrage!"),
            html.Button('Umfrage abschliessen', id='abschliessen')
        ]
        '''
