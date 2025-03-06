# -*- coding: utf-8 -*-
#Notiz wichtig: Beim Speichern eines Dicts als Session in Flask werden die Keys von int in String umgewandelt
##ganz ueble Fehlerquelle
#Notiz wichtig: TEXT_FIELDS in der print_session_data() Methode und beim Aufruf von session['TEXT-FIELDS'] und generell TEXT_FIELDS 
#koennen nur aufgerufen werden, wenn der Nutzer authentifiziert ist und die session nicht frisch gecleart worden ist.
#Notiz wichtig: redis speichert die Schluessel und Werte als Bytes-Objekte, als b''Key':'Value'

#Notiz WICHTIG WICHTIG: BEI SESSION-INITIALISIERUNG MUESSEN SAEMTLICHE EINTRAEGE NOCHMAL UEBERPRUEFT WERDEN, OB SIE NUN KORREKT SIND --> ANGLEICHEN AN globales TEXT_FIELDS

#Refaktorierungsschritte:
#1. Imports
#2. Flask App: Basiskonfiguration - Authentifizierung, Session-Clearing, Initialisierung Session-Variablen
#3. Debug-Bereich Flask-Basiskonfiguration 
#4. Flask App (Session) und Redis: Speichern und Laden der Textfelder - Struktur verbessert
#5. Wrapper-Methode eingefuegt, die in Session und Redis gleichzeitig speichert - neu eingefuegt
#6. Globale Strukturvariablen und -datenstrukturen wieder eingefuegt - dort lag wahrscheinlich der fatale Fehler: Eintrag 20 war doppelt vorhanden
#und ein paar weitere Inkonsistenzen
####################


##########Alte, rausgeschmissene Imports
#from codecs import backslashreplace_errors

#import dash
#from dash import Dash, html, dcc, Input, Output, State, no_update, callback_context, ctx
#import dash.dash_table
#from dash.exceptions import NonExistentEventException, PreventUpdate

#import flask_socketio
#from socketio import Client
#from flask_session import Session


#import sys
#import io
#import uuid

#import threading
#import multiprocessing
#from queue import Queue

#import webbrowser
#import requests

#import numpy as np
#import matplotlib.pyplot as plt
#from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

#from transformers import pipeline

#Imports fuer die Zusatzfenster
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


#Imports
from xmlrpc.client import boolean
from h11 import SERVER

import dash_bootstrap_components as dbc
from flask import Flask, request, jsonify, session, render_template_string, redirect, copy_current_request_context, has_request_context, current_app, render_template

from flask_socketio import SocketIO

import redis

import os
import time
from datetime import timedelta
import re

#################### Globale Datenstrukturen und Variablen, die die Struktur der Dash App bestimmen 

#IP-Adresse des Servers
host_ip = "http://127.0.0.1"
dash_port = "8050"
flask_port = "5000" #Der Port, auf dem sich diese Flask_Module.py befindet





#letzte_session_ID

#def store_session_data(session_id, data):
#    global_sessions[session_id] = data#

#def get_session_data(session_id):
#    return global_sessions.get(session_id)

#####Globale Datenstrukturen und Variablen: Debug-Methoden
def platzhaltermethode():
    print("Hallo Moto")

#####Globale Variablen - Dash
# Verzeichnis zu den Bildern (die 130 PDF-Seiten, die der Hintergrund sind)
ASSETS_DIR = "./pages_7"

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
    16: [
        {"id": "text-16-1", "value": None, "x": 51, "y": 58, "width": 93, "height": 27.0, "changable": True},
        {"id": "text-16-2", "value": None, "x": 51, "y": 71.5, "width": 93, "height": 27.0, "changable": True},
        {"id": "text-16-3", "value": None, "x": 51, "y": 87, "width": 93, "height": 31.0, "changable": True},
        {"id": "text-16-4", "value": None, "x": 51, "y": 103.4, "width": 93, "height": 31.0, "changable": True},
    ],
    18: [
        {"id": "text-18-1", "value": "Stell wir vor, hier waeren deine Audiodaten klassifiziert worden.", "x": 37, "y": 91, "width": 65, "height": 58.0, "changable": False},
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

        {"id": "text-43-2", "value": None, "x": 33, "y": 82, "width": 25, "height": 18.0, "changable": True},
        {"id": "text-43-3", "value": None, "x": 41, "y": 82, "width": 25, "height": 18.0, "changable": True},
        {"id": "text-43-4", "value": None, "x": 49, "y": 82, "width": 25, "height": 18.0, "changable": True},
        {"id": "text-43-5", "value": None, "x": 57, "y": 82, "width": 25, "height": 18.0, "changable": True},
        {"id": "text-43-6", "value": None, "x": 65, "y": 82, "width": 25, "height": 18.0, "changable": True},
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
        {"id": "text-50-3", "value": None, "x": 52.5, "y": 40, "width": 95, "height": 35.0, "changable": True},
        {"id": "text-50-4", "value": None, "x": 52.5, "y": 62, "width": 95, "height": 45.0, "changable": True},
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
        {"id": "text-100-1", "value": None, "x": 50, "y": 50, "width": 80, "height": 30.0, "changable": True},
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
        {"id": "checkbox-42-3", "x": 50, "y": 29, "scale": 2.5, "checked": False},
        {"id": "checkbox-42-4", "x": 50, "y": 31.8, "scale": 2.5, "checked": False, "changable": True},
    ],
    43: [
        {"id": "checkbox-43-1", "x": 60, "y": 37, "scale": 2.5, "checked": False, "changable": True},
        {"id": "checkbox-43-2", "x": 60, "y": 39.8, "scale": 2.5, "checked": False, "changable": True},
        {"id": "checkbox-43-3", "x": 60, "y": 42.7, "scale": 2.5, "checked": False, "changable": True},
    ],
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
        #{"id": "button-16-1", "x": 70, "y": 12, "label": "Klick mich", "color": "primary", "background_color" : "grey" , "method": platzhaltermethode},
    ],

    18: [
        {"id": "button-18-1", "x": 50, "y": 22.5, "label": "Audio Aufnehmen", "color": "success", "background_color" : "grey" , "method": platzhaltermethode},
        {"id": "button-18-2", "x": 50, "y": 28.5, "label": "Audio Beenden", "color": "success", "background_color" : "grey" , "method": platzhaltermethode},
    ],
    20: [
        #{"id": "button-20-1", "x": 5, "y": 15, "label": "OK", "color": "success", "background_color" : "grey" , "method": platzhaltermethode},
    ],
    21: [ #Zweckloesung: hier mussten ganz viele Unicode Leerzeichen eingefuegt werden, damit der Button laenger gestreckt ist und sich ueber die gesamte URL erstreckt
        {"id": "button-21-1", "x": 20.1, "y": 13.1, "label": "\u2003\u2003\u2003\u2003\u2003\u2003\u2003\u2003\u2003\u2003\u2003\u2003\u2003\u2003\u2003\u2003\u2003", "color": "blue", "background_color" : "rgba(128,128,128,0.5)" , "method": platzhaltermethode},
    ],
    33: [
        {"id": "button-33-1", "x": 12.5, "y": 18.5, "label": "Zeichenfenster oeffnen", "color": "blue", "background_color" : "grey" , "method": platzhaltermethode},
    ],
    42: [
        {"id": "button-42-1", "x": 12.5, "y": 43.5, "label": "Zeichenfenster oeffnen", "color": "blue", "background_color" : "grey" , "method": platzhaltermethode},
    ],
    43: [
        {"id": "button-43-1", "x": 10, "y": 83.5, "label": "Fenster oeffnen", "color": "blue", "background_color" : "grey" , "method": platzhaltermethode},
    ],
    69: [
        {"id": "button-69-1", "x": 12.5, "y": 83.5, "label": "Zeichenfenster oeffnen", "color": "blue", "background_color" : "grey" , "method": platzhaltermethode},
    ],
    94: [
        {"id": "button-94-1", "x": 10, "y": 34.5, "label": "Analysieren", "color": "blue", "background_color" : "grey" , "method": platzhaltermethode},
    ],
}

#Serverseitiger Zwischenspeicher - ist keine gute Loesung, aber weil die flask_session ja nur Probleme macht, gibt es keine Alternative
#Ausbau-Ideen, damit mehrere Nutzer gleichzeitig arbeiten koennen (ist aber irrelevant): den zwischenspeicher als Klasse bauen und 
#jeden Nutzer als Objekt. Dann eindeutigen Identifier einbauen und so weiter
session_zwischenspeicher = {
    'session_id' : None,
    'current_page' : None,
    'current_url' : None,
    'TEXT_FIELDS' : {},
    'CHECK_BOXES' : {},
    'initialized' : False,
    }



####################Alles, was mit Flask, Flask-SocketIO und Redis zu tun hat
# Flask App als API fuer clientseitige Fenster
flask_app = Flask(__name__)

# Flask App als API fuer clientseitige Fenster
flask_app.secret_key = 'supersecretkey'
flask_app.config['SESSION_TYPE'] = 'redis'  # Konfiguriere die Session, um Redis zu verwenden
flask_app.config['SESSION_PERMANENT'] = True  # Optional: Session nicht permanent machen
flask_app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=480)
flask_app.config['SESSION_USE_SIGNER'] = True  # Optional: Session-Cookie signieren
redis_client = flask_app.config['SESSION_REDIS'] = redis.StrictRedis(host='188.245.219.175', port=6379, db=0, password="996340Fabi#PbUni")  # Konfiguriere Redis
#Redis Client
redis_client = flask_app.config['SESSION_REDIS']

#Einrichtung eines Sockets, um effizient Daten hin zum Port 8050 zu senden
#Man kann via flasksocketio_socket.emit('message_to_dash', message) eine Nachricht ruebersenden
flasksocketio_hostsocket = SocketIO(flask_app, cors_allowed_origins="*", logger=True, engineio_logger=True)

@flasksocketio_hostsocket.on('connect')
def connect():
    print("connect: Ein Client hat sich zur Flask-App (Port 5000) verbunden!")


#################### Javascript-Funktionalitaeten fuer die externen Fenster hier einbauen --> Aufruf via link moeglich
#####Flask Routen
@flask_app.route('/zeichenfenster')
def zeichenfenster():
    return render_template('zeichenfenster.html')   

@flask_app.route('/zeichenfenster_ohne_ks')
def zeichenfenster_ohne_ks():
    return render_template('zeichenfenster_ohne_ks.html')  

@flask_app.route('/audioaufnahme')
def audioaufnahme():
    return render_template('audioaufnahme.html')  

@flask_app.route('/yt_kommentaranalyse')
def yt_kommentaranalse():
    return render_template('yt_kommentaranalyse.html')  

@flask_app.route('/kameraanalyse')
def kameraanalyse():
    return render_template('kameraanalyse.html')  



##########
#####Flask: Hilfsmethoden
# Generierung des Pseudonyms aus Nutzerdaten
def generate_session_id(mother_name, birth_place, birth_year):
    return f"{mother_name[:2].upper()}{birth_place[:2].upper()}{birth_year}"

#####Redis: Hilfsmethoden
# Laden aller Textfeld-Keys eines Users anhand der Session-ID (welche im Notfall aus dem session Speicher geladen wird) 
# Rueckgabe: Liste mit einem Element drin, naemlich dem Textfeld_Key im Byte-Format
def redis_load_text_field_keys(session_id=None):
    try:
        if session_id == None and 'session_id' in session:
            session_id = session['session_id']
        elif session_id == None and 'session_id' in session_zwischenspeicher:
            try:
                session_id = session_zwischenspeicher['session_id']
            except Exception as e:
                print("redis_load_text_field_id: Ein Fehler ist beim Versuch des Ziehens der session_id passiert. Exception: ", e)
        elif session_id == None:
            return None
    except Exception as e:
        print("redis_load_text_field_id: Folgende Exception ist aufgetreten: ", e)
    user_redis_keys = redis_client.keys(f'session:{session_id}:page:*:text_field_id:')
    return user_redis_keys

# Laden aller Checkbox-Keys eines Users anhand der User-ID; Rueckgabe: Liste mit einem Element drin, naemlich dem Checkbox_Key im Byte-Format
def redis_load_checkbox_keys(session_id=None):
    try:
        if session_id == None and 'session_id' in session:
            session_id = session['session_id']
        elif session_id == None and 'session_id' in session_zwischenspeicher:
            try:
                session_id = session_zwischenspeicher['session_id']
            except Exception as e:
                print("redis_load_text_field_id: Ein Fehler ist beim Versuch des Ziehens der session_id passiert. Exception: ", e)
        else:
            return None
    except Exception as e:
        print("redis_load_text_field_id: Folgende Exception ist aufgetreten: ", e)
    user_redis_keys = redis_client.keys(f'session:{session_id}:page:*:check_box_id:')
    return user_redis_keys

# um Redis --> Zwischenspeicher zu ermoeglichen
def redis_load_all_text_fields():
    TEXT_FIELDS = {}
    
    # Redis-Schluessel fuer die Textfelder holen
    text_field_keys = redis_load_text_field_keys()
    if not text_field_keys:
        return None
    
    for redis_key in text_field_keys:
        #Hole die Seitenzahl aus dem redis_key heraus und ergaenze ein dict im TEXT_FIELD fuer die Seite
        try:
            redis_key_decoded = redis_key.decode('utf-8')
            #print("redis_load_all_text_fields: REDIS KEY ERMITTELN: redis_key: ", redis_key_decoded)
            page_matching = re.search(r'page:(\d+):', redis_key_decoded)
            page = int(page_matching.group(1)) if page_matching else None
            #print("redis_load_all_text_fields: REDIS KEY ERMITTELN: page: ", page)
            if str(page) not in TEXT_FIELDS:
                TEXT_FIELDS[str(page)] = {}
        except Exception as e:
            print("redis_load_all_text_fields: Ein Fehler ist aufgetreten, die Seite konnte nicht aus dem redis_key ermittelt werden. Exception: ", e)
            return
    
        # Lade alle Felder und Werte aus dem Redis-Hash
        text_fields_raw = redis_client.hgetall(redis_key)
    
        # Dekodiere die Bytestrings und fuege sie in das Dictionary ein
        text_fields = {key.decode('utf-8'): value.decode('utf-8') for key, value in text_fields_raw.items()}
    
        # Aktualisiere den Zwischenspeicher
        for text_field_id in text_fields:
            TEXT_FIELDS[str(page)][text_field_id] = text_fields[text_field_id]
    return TEXT_FIELDS


def redis_load_all_checkboxes():
    CHECK_BOXES = {}
    
    # Redis-Schluessel fuer die Textfelder holen
    checkbox_keys = redis_load_checkbox_keys()
    if not checkbox_keys:
        return None
    
    for redis_key in checkbox_keys:
        #Hole die Seitenzahl aus dem redis_key heraus und ergaenze ein dict im TEXT_FIELD fuer die Seite
        try:
            redis_key_decoded = redis_key.decode('utf-8')
            #print("redis_load_all_text_fields: REDIS KEY ERMITTELN: redis_key: ", redis_key_decoded)
            page_matching = re.search(r'page:(\d+):', redis_key_decoded)
            page = int(page_matching.group(1)) if page_matching else None
            #print("redis_load_all_text_fields: REDIS KEY ERMITTELN: page: ", page)
            if str(page) not in CHECK_BOXES:
                CHECK_BOXES[str(page)] = {}
        except Exception as e:
            print("redis_load_all_checkboxes: Ein Fehler ist aufgetreten, die Seite konnte nicht aus dem redis_key ermittelt werden. Exception: ", e)
            return
    
        # Lade alle Felder und Werte aus dem Redis-Hash
        checkboxes_raw = redis_client.hgetall(redis_key)
    
        # Dekodiere die Bytestrings und fuege sie in das Dictionary ein
        checkboxes = {key.decode('utf-8'): value.decode('utf-8') for key, value in checkboxes_raw.items()}
    
        # Aktualisiere den Zwischenspeicher
        for checkbox_id in checkboxes:
            CHECK_BOXES[str(page)][checkbox_id] = checkboxes[checkbox_id]
    return CHECK_BOXES

'''def all_checkboxes_to_zwischenspeicher():
    global session_zwischenspeicher
    
    # Redis-Schluessel fuer den Checkboxen holen
    checkbox_keys = redis_load_checkbox_keys()
    if not checkbox_keys:
        return
    
    redis_key = checkbox_keys[0]
    
    # Lade alle Felder und Werte aus dem Redis-Hash
    text_fields_raw = redis_client.hgetall(redis_key)
    
    # Dekodiere die Bytestrings und fuege sie in das Dictionary ein
    checkboxes = {key.decode('utf-8'): value.decode('utf-8') for key, value in text_fields_raw.items()}
    
    # Aktualisiere den Zwischenspeicher
    session_zwischenspeicher['CHECK_BOXES'] = checkboxes'''

##########
#####Flask: Debugmethoden
@flask_app.before_request
def print_session_data():
    print("print_session_data: Wurde aufgerufen.")
    global session_zwischenspeicher
    print("DATEN DER SESSION:")
    print("Session ID: ", session_zwischenspeicher['session_id'] if 'session_id' in session_zwischenspeicher else None)
    print("Current Page: ", session_zwischenspeicher['current_page'] if 'current_page' in session_zwischenspeicher else None)
    print("Current URL: ", session_zwischenspeicher['current_url'] if 'current_url' in session_zwischenspeicher else None)
    print("Initialized: ", session_zwischenspeicher['initialized'] if 'initialized' in session_zwischenspeicher else None)
    print("TEXT-FIELDS: (Zwischenspeicher) ", session_zwischenspeicher['TEXT_FIELDS'] if 'TEXT_FIELDS' in session_zwischenspeicher else None)
    print("CHECK-BOXES: (Zwischenspeicher)", session_zwischenspeicher['CHECK_BOXES'] if 'CHECK_BOXES' in session_zwischenspeicher else None)
    print("REDIS USERKEYS (redis_load_text_field_keys): ", redis_load_text_field_keys())
    print("REDIS CHECKBOXES (redis_load_checkbox_keys): ", redis_load_checkbox_keys())
    print("redis_load_all_text_fields: ", redis_load_all_text_fields())
    #global flasksocketio_hostsocket
    #print("TESTEN DES HOSTSOCKETS - Verbundene Clients. ")
    #try:
    #    flasksocketio_hostsocket.emit('textfields_to_dash', session_zwischenspeicher["TEXT_FIELDS"])
    #    print("flasksocketio_hostsocket: EMIT WURDE GETESTET")
    #except Exception as e:
    #    print("HOSTSOCKET: Folgender Fehler ist aufgetreten: ", e)
    #print("REDIS TEXTFELD BEI ID 'text-16-1':", redis_load_text_field('text-16-1'))
    #war noetig, um festzustellen, dass die Keys in TEXT_FIELDS bei Speicherung als Redis-Element in Strings umgewandelt werden
    #print("Typ der Keys des TEXT-FIELDS: ",(session['TEXT_FIELDS'].keys()))
    #session_save_text_field(value="HALLLOOOO", page_number=16, text_field_id="text-16-2")
    #print("Geladener Text aus Redis: ", session_load_text_field(text_field_id="text-16-2"))
    #print("Lade Textfeld aus Session: ", session_load_text_field(text_field_id="text-16-1"))#'''

'''@flask_app.before_request
def print_session_data():
    print("DATEN DER SESSION:")
    print("Daten fuer Session ID: ", session['session_id'] if 'session_id' in session else None)
    print("Current Page: ", session['current_page'] if 'current_page' in session else None)
    print("Current URL: ", session['current_url'] if 'current_url' in session else None)
    print("Initialized: ", session['initialized'] if 'initialized' in session else None)
    print("TEXT-FIELDS: ", session['TEXT_FIELDS'] if 'TEXT_FIELDS' in session else None)
    print("CHECK-BOXES: ", session['CHECK_BOXES'] if 'CHECK_BOXES' in session else None)'''


#@flask_app.before_request
def print_das_gezogene_textfeld_aus_dem_sessionspeicher():
    #Ueberprueft, ob man ein Textfeld mithilfe der get_text_field_content abrufen kann
    textfield_content = session_load_text_field('text-5-1', page=None, on_same_page = False)
    print("TEXTFIELD 'text-5-1' Wert: ", textfield_content)

# Test-Route fuer Redis
@flask_app.route('/test-redis')
def test_redis():
    try:
        global session_zwischenspeicher
        #redis_client = flask_app.config['SESSION_REDIS']
        visits = redis_client.incr('visits')
        info = redis_client.info()
        session_id = session_zwischenspeicher['session_id']
        all_redis_keys = redis_client.keys('*')
        user_redis_keys = redis_client.keys(f'session:{session_id}:*')

        #key-value pairs der redis schluessel ermitteln
        key_value_pairs = {}
        values = []

        for key in user_redis_keys:
            value = redis_client.hgetall(key)
            decoded_value = {k.decode('utf-8'): v.decode('utf-8') for k, v in value.items()} if value else None
            key_value_pairs[key] = decoded_value
            values.append(decoded_value)
            
        connection_data = {
            #Redis-Parameter
            'host': redis_client.connection_pool.connection_kwargs['host'],
            'port': redis_client.connection_pool.connection_kwargs['port'],
            'db': redis_client.connection_pool.connection_kwargs['db'],
            'redis_version': info['redis_version'],
            'connected_clients': info['connected_clients'],
            'used_memory_human': info['used_memory_human'],
            'total_connections_received': info['total_connections_received'],
            'uptime_in_seconds': info['uptime_in_seconds'],
            #Session-Variablen der Flask-Session
            'session_id' : session['session_id'] if 'session_id' in session else None,
            'session_initialized': session['initialized'] if 'initialized' in session else None,
            'current_url' : session['current_url'] if 'current_url' in session else None,
            'current_page' : session['current_page'] if 'current_page' in session else None,
            'TEXT_FIELDS' : session['TEXT_FIELDS'] if 'TEXT_FIELDS' in session else None,
            'CHECK_BOXES' : session['CHECK_BOXES'] if 'CHECK_BOXES' in session else None,

            #Session-Zwischenspeicher-Variablen (global) der Flask-Session
            'session_zwischenspeicher_id' : session_zwischenspeicher['session_id'] if 'session_id' in session_zwischenspeicher else None,
            'session_zwischenspeicher_initialized': session_zwischenspeicher['initialized'] if 'initialized' in session_zwischenspeicher else None,
            'current_zwischenspeicher_url' : session_zwischenspeicher['current_url'] if 'current_url' in session_zwischenspeicher else None,
            'current_zwischenspeicher_page' : session_zwischenspeicher['current_page'] if 'current_page' in session_zwischenspeicher else None,
            'zwischenspeicher_TEXT_FIELDS' : session_zwischenspeicher['TEXT_FIELDS'] if 'TEXT_FIELDS' in session_zwischenspeicher else None,
            'zwischenspeicher_CHECK_BOXES' : session_zwischenspeicher['CHECK_BOXES'] if 'CHECK_BOXES' in session_zwischenspeicher else None,

            #In Redis gespeicherte Keys
            'all_redis_keys' : all_redis_keys,
            'user_redis_keys' : user_redis_keys,
            'key_value_pairs' : key_value_pairs,
            'values' : values


            #'key_value_pairs' : key_value_pairs
        }
        
        return f'''Redis funktioniert. Anzahl der Besuche: {visits}
        <br><br>
        Verbindungsdaten:
        <br>
        Host: {connection_data['host']}
        <br>
        Port: {connection_data['port']}
        <br>
        Datenbank: {connection_data['db']}
        <br>
        Redis-Version: {connection_data['redis_version']}
        <br>
        Verbundene Clients: {connection_data['connected_clients']}
        <br>
        Verwendeter Speicher: {connection_data['used_memory_human']}
        <br>
        Gesamtanzahl der Verbindungen: {connection_data['total_connections_received']}
        <br>
        Uptime (Sekunden): {connection_data['uptime_in_seconds']}
        <br>
        <br>
        <br>
        ::::Session-Variablen::::
        <br>
        Session der Flask-App: {connection_data['session_id']}
        <br>
        Session_initialized: {connection_data['session_initialized']}
        <br>
        Current_url: {connection_data['current_url']}
        <br>
        Current_page: {connection_data['current_page']}
        <br>
        Text_fields: <br> {connection_data['TEXT_FIELDS']}
        <br>
        Check_Boxes: <br> {connection_data['CHECK_BOXES']}
        <br>
        <br>
        <br>
        ::::Session-Zwischenspeicher-Variablen (global)::::
        <br>
        Session der Flask-App: {connection_data['session_zwischenspeicher_id']}
        <br>
        Session_initialized: {connection_data['session_zwischenspeicher_initialized']}
        <br>
        Current_url: {connection_data['current_zwischenspeicher_url']}
        <br>
        Current_page: {connection_data['current_zwischenspeicher_page']}
        <br>
        Text_fields: <br> {connection_data['zwischenspeicher_TEXT_FIELDS']}
        <br>
        Check_Boxes: <br> {connection_data['zwischenspeicher_CHECK_BOXES']}
        <br>
        <br>
        <br>
        ::::Alle vorhandenen Redis-Schluessel des Nutzers::::
        <br>
        Redis-Schluessel: {connection_data['all_redis_keys']}
        <br>
        <br>
        Redis-Nutzer-Schluessel: {connection_data['user_redis_keys']}
        <br>
        <br>
        Redis-Schluessel-und-Werte: {connection_data['key_value_pairs']}
        <br>
        <br>
        Redis-Werte: {connection_data['values']}

        '''
    except Exception as e:
        return f'Redis-Fehler: {str(e)}'


# Test-Route fuer Redis
@flask_app.route('/')
def startseite():
    return redirect('/authenticate')

##########
#####Flask: Authentifizierungsseite
@flask_app.route('/authenticate', methods=['GET', 'POST'])
def authenticate():
    print("authentificate wurde aufgerufen", flush=True)
    global session_zwischenspeicher
    # Session-Variablen initialisieren, falls noch nicht geschehen
    if 'initialized' not in session or session['initialized'] == False or session['initialized'] == None or 'initialized' not in session:
        session['current_url'] = f"{host_ip}:{flask_port}/authenticate" #HIER IP UEBERARBEITET"http://127.0.0.1:5000/authenticate"
        session['current_page'] = None
        session['session_id'] = None  # Initialisiere session_id mit None
        if 'TEXT_FIELDS' not in session:
            session['TEXT_FIELDS'] = redis_load_all_text_fields()
        if 'TEXT_FIELDS' not in session:
            session['CHECK_BOXES'] = redis_load_all_checkboxes()
        session['initialized'] = False

    # In Redis gespeicherte Textfelder holen in den Zwischenspeicher
    if 'TEXT_FIELDS' in session_zwischenspeicher:
        session_zwischenspeicher['TEXT_FIELDS'] = redis_load_all_text_fields()
    # In Redis gespeicherte Checkboxen holen
    if 'CHECK_BOXES' in session_zwischenspeicher:
        session_zwischenspeicher['CHECK_BOXES'] = redis_load_all_checkboxes()
    #Daten an Dash weitersenden
    # In Redis gespeicherte Textfelder holen in den Zwischenspeicher
    if 'TEXT_FIELDS' in session_zwischenspeicher:
        send_textfields_to_dash()
    # In Redis gespeicherte Checkboxen holen
    if 'CHECK_BOXES' in session_zwischenspeicher:
        send_checkboxes_to_dash()
    if 'initialized' in session and session['initialized'] == True and session['session_id'] is not None:
        send_session_id_to_dash() #ist nicht 100% durchdacht
        return redirect(host_ip + ":" + dash_port + '/1')

    if session['initialized'] == False and session['session_id'] == None:
        if request.method == 'POST':
            mother_name = request.form.get('mother_name', '')[:2]
            birth_place = request.form.get('birth_place', '')[:2]
            birth_year = request.form.get('birth_year', '')
    
            if len(mother_name) == 2 and len(birth_place) == 2 and birth_year.isdigit():
                session['session_id'] = generate_session_id(mother_name, birth_place, birth_year)
                print("SESSION_ID!!!!: ", session['session_id'])
                session_zwischenspeicher['session_id'] = session['session_id']
                send_session_id_to_dash()
                session['initialized'] = True
                return redirect(host_ip + ":" + dash_port + '/1')

    return render_template_string('''
        <form method="post">
            Vorname der Mutter (2 Buchstaben): <input name="mother_name"><br>
            Geburtsort (2 Buchstaben): <input name="birth_place"><br>
            Geburtsjahr: <input name="birth_year"><br>
            <input type="submit" value="Login">
        </form>
    ''')



##### Session loeschen (Logout)
@flask_app.route('/clear-session')
def clear_session():
    global session_zwischenspeicher
    session['initialized'] = False
    session.clear()

    session_zwischenspeicher = {
    'session_id' : None,
    'current_page' : None,
    'current_url' : None,
    'TEXT_FIELDS' : {},
    'CHECK_BOXES' : {},
    'initialized' : None,
    }
    return jsonify({'status': 'success', 'message': 'Ausgeloggt. See you again.'})#redirect(host_ip + ":" + flask_port + "/authenticate")#jsonify({'status': 'success', 'message': 'Ausgeloggt. See you again.'}) #redirect(host_ip + ":" + flask_port + "/authenticate")


#####Methoden zum Auslesen und Schreiben der Sessiondaten
#Currrent-url und currrent-page updaten
@flask_app.before_request
def update_session_current_url():
    """
    Speichert die aktuelle URL und die aktuelle Seite direkt in der Session-Konfiguration.
    """
    #Speicherung current_url
    current_url = request.url#request.headers.get('Referer')
    #print("CURRENT URL:    ", current_url, "Typ der URL:  ", type(current_url))
    session['current_url'] = current_url
    # Extrahiere die aktuelle Seite aus der URL
    try:
        if current_url != None:
            page_str = current_url.strip('/').split('/')[-1]
            print("SEITE (stringformat), AUF DER WIR SIND: ", page_str)
            try:
                page = int(page_str)
            except Exception: #zuerst: ValueError
                page = None
        else:
            print("Der USER ist auf keiner Seite.")
        if page != None:
            # Speicherung current_page
            if 1 <= page <= 150:
                session['current_page'] = page
                #print("CURRENT PAGE WURDE INNERHALB DER SESSION ANGEPASST. Die Seite ist: ", session['current_page'], " fuer SESSION-ID: ", session["session_id"])
            else:
                session['current_page'] = None
    except Exception:
        session['current_page'] = None

'''@flask_app.before_request
def update_text_fields_from_redis():
    #if Statement: Erstellt alle Textfelder
    if 'TEXT_FIELDS' not in session or session['TEXT_FIELDS'] == {}:
        session['TEXT_FIELDS'] = {}
        print('update_text_fields_from_redis: if-Teil wurde aufgerufen')
        for page in TEXT_FIELDS:
            for text_field_id in TEXT_FIELDS[page]:
                value = redis_load_text_field(text_field_id)
                session['TEXT_FIELDS'][str(page)][text_field_id] = value
    #Else Statement: Updatet nur die Textfelder der current_page auf der wir sind
    else:
        print('update_text_fields_from_redis: else-Teil wurde aufgerufen')
        current_page = session['current_page']
        if current_page in TEXT_FIELDS:
            for text_field_id in TEXT_FIELDS[str(current_page)]:
                    value = redis_load_text_field(text_field_id)
                    session['TEXT_FIELDS'][str(page)][text_field_id] = value'''
        

###########Session <-> Code: Textfelder Speichern Laden

#####Flask: textfield mithilfe einer textfield-id (und ) aus der Session rausholen und returnen
#Wenn on_same_page = True oder page != None ist, wird der Textfeldeintrag effizienter gesucht.
#wichtig: page muss als Integer uebergeben werden; wird dann in string umgewandelt
def session_save_text_field(value, text_field_id, page_number=None):
    if page_number == None:
        try:
            page_matching = re.search(r'-(\d+)-', text_field_id)
            page_number = int(page_matching.group(1)) if page_matching else None
        except Exception as e:
            print("Ein Fehler ist aufgetreten, die Seite des Textfeldes konnte nicht aus der textfield_id heraus ermittelt werden. Exception: ", e)
            return
    #Speicherung in der Nutzersession
    if 'session_id' in session:
        session_id = session['session_id']
        if 'TEXT_FIELDS' not in session:
            session['TEXT_FIELDS'] = {}
        try:
            # Speichere den Wert in der Session
            if str(page_number) not in session['TEXT_FIELDS']:
                session['TEXT_FIELDS'][str(page_number)] = {}
            session['TEXT_FIELDS'][str(page_number)][text_field_id] = value
            print(f"session_save_text_field: Erfolg: Wert - {value} - korrekt in der Session gespeichert.")
        except Exception as e:
            print(f"Fehler: ist aufgetreten. Folgende Exception: {e}")
            return

    #Speicherung im Zwischenspeicher
    if 'session_id' in session_zwischenspeicher:
        session_id = session_zwischenspeicher['session_id']
        if 'TEXT_FIELDS' not in session_zwischenspeicher:
            session_zwischenspeicher['TEXT_FIELDS'] = {} # Fall der nicht auftreten sollte
        try:
            # Speichere den Wert in der Session
            if str(page_number) not in session_zwischenspeicher['TEXT_FIELDS']:
                session_zwischenspeicher['TEXT_FIELDS'][str(page_number)] = {}
            session_zwischenspeicher['TEXT_FIELDS'][str(page_number)][text_field_id] = value
            print(f"session_save_text_field: Erfolg: Wert - {value} - korrekt in der Session gespeichert.")
        except Exception as e:
            print(f"Fehler: ist aufgetreten. Folgende Exception: {e}")
            return

    '''if 'session_id' not in session:
        #print("Fehler: Session-ID nicht in Session")
        return
    session_id = session['session_id']
    if page_number == None:
        try:
            page_matching = re.search(r'-(\d+)-', text_field_id)
            page_number = int(page_matching.group(1)) if page_matching else None
        except Exception as e:
            print("Ein Fehler ist aufgetreten, die Seite des Textfeldes konnte nicht aus der textfield_id heraus ermittelt werden. Exception: ", e)
            return
    try:
        # Speichere den Wert in der Session
        session['TEXT_FIELDS'][str(page_number)][text_field_id] = value
        print(f"Erfolg: Wert - {value} - korrekt in der Session gespeichert.")
        return
    except Exception as e:
        print(f"Fehler: ist aufgetreten. Folgende Exception: {e}")
        return'''


def session_load_text_field(text_field_id, page_number=None, on_same_page = False):
    """
    Holt den Inhalt eines Textfelds aus der Session basierend auf der Textfeld-ID.

    :param text_field_id: Die ID des Textfelds, z.B. 'text-5-1'
    :return: Der gespeicherte Inhalt des Textfelds oder None, wenn nicht vorhanden
    """
    if on_same_page == False:
        if 'TEXT_FIELDS' not in session:
            return None  # Falls die TEXT_FIELDS-Session nicht existiert
        # Suche in allen Seiten nach der Textfeld-ID
        for page_data in session['TEXT_FIELDS'].values():
            if text_field_id in page_data:
                return page_data[text_field_id]
        return None
    #Benutzt die page, um sich das Textfeld rauszuziehen
    if page_number != None:
        if 'TEXT_FIELDS' not in session:
            return None  # Falls die TEXT_FIELDS-Session nicht existiert
        # Ziehe direkt den Value direkt aus dem richtigen dict im Speicher
        page_data = session['TEXT_FIELDS'][str(page_number)]
        if text_field_id in page_data:
                return page_data[text_field_id]
        return None
    #Zieht sich die page aus dem Session-Speicher und holt danach direkt den korrekten Value
    if on_same_page == True and session['current_page'] != None:
        if 'TEXT_FIELDS' not in session:
            return None
        page = session['current_page']
        page_data = session['TEXT_FIELDS'][str(page)]
        if text_field_id in page_data:
                return page_data[text_field_id]
        return None
    if page_number == None: #holt sich die page_number dann aus der Textfeld-ID oder versucht es und returnt sonst None
        try:
            page_matching = re.search(r'-(\d+)-', text_field_id)
            page_number = int(page_matching.group(1)) if page_matching else None
        except Exception as e:
            print("Ein Fehler ist aufgetreten, die Seite des Textfeldes konnte nicht aus der textfield_id heraus ermittelt werden. Exception: ", e)
            return None
        page_data = session['TEXT_FIELDS'][str(page_number)]
        if text_field_id in page_data:
                return page_data[text_field_id]
        return None



###########Session <-> Code: Textfelder Speichern Laden
def session_save_checkbox(value, checkbox_id, page_number=None):
    if page_number == None:
        try:
            page_matching = re.search(r'-(\d+)-', checkbox_id)
            page_number = int(page_matching.group(1)) if page_matching else None
        except Exception as e:
            print("Ein Fehler ist aufgetreten, die Seite des Textfeldes konnte nicht aus der textfield_id heraus ermittelt werden. Exception: ", e)
            return

    #Speicherung in der Nutzersession
    if 'session_id' in session:
        session_id = session['session_id']
        if 'CHECK_BOXES' not in session:
            session['CHECK_BOXES'] = {}
        try:
            # Speichere den Wert in der Session
            if str(page_number) not in session['CHECK_BOXES']:
                session['CHECK_BOXES'][str(page_number)] = {}
            session['CHECK_BOXES'][str(page_number)][checkbox_id] = value
            print(f"session_save_check_box: Erfolg: Wert - {value} - korrekt in der Session gespeichert.")
        except Exception as e:
            print(f"Fehler: ist aufgetreten. Folgende Exception: {e}")
            return

    #Speicherung im Zwischenspeicher
    if 'session_id' in session_zwischenspeicher:
        session_id = session_zwischenspeicher['session_id']
        if 'CHECK_BOXES' not in session_zwischenspeicher:
            session_zwischenspeicher['CHECK_BOXES'] = {}
        try:
            # Speichere den Wert in der Session
            if str(page_number) not in session_zwischenspeicher['CHECK_BOXES']:
                session_zwischenspeicher['CHECK_BOXES'][str(page_number)] = {}
            session_zwischenspeicher['CHECK_BOXES'][str(page_number)][checkbox_id] = value
            print(f"session_save_check_box: Erfolg: Wert - {value} - korrekt in der Session gespeichert.")
        except Exception as e:
            print(f"Fehler: ist aufgetreten. Folgende Exception: {e}")
            return
    return


def session_load_checkbox(checkbox_id, page_number=None, on_same_page=False):
    """
    Holt den Zustand einer Checkbox aus der Session basierend auf der Checkbox-ID.

    :param checkbox_id: Die ID der Checkbox, z.B. 'checkbox-5-1'
    :return: Der gespeicherte Zustand der Checkbox (True/False) oder None, wenn nicht vorhanden
    """
    if on_same_page == False:
        if 'CHECK_BOXES' not in session:
            return None  # Falls die CHECK_BOXES-Session nicht existiert
        # Suche in allen Seiten nach der Checkbox-ID
        for page_data in session['CHECK_BOXES'].values():
            if checkbox_id in page_data:
                return page_data[checkbox_id]
        return None
    
    if page_number != None:
        if 'CHECK_BOXES' not in session:
            return None
        # Ziehe direkt den Value direkt aus dem richtigen dict im Speicher
        page_data = session['CHECK_BOXES'][str(page_number)]
        if checkbox_id in page_data:
            return page_data[checkbox_id]
        return None
    
    if on_same_page == True and session['current_page'] != None:
        if 'CHECK_BOXES' not in session:
            return None
        page = session['current_page']
        page_data = session['CHECK_BOXES'][str(page)]
        if checkbox_id in page_data:
            return page_data[checkbox_id]
        return None
    
    if page_number == None:
        try:
            page_matching = re.search(r'-(\d+)-', checkbox_id)
            page_number = int(page_matching.group(1)) if page_matching else None
        except Exception as e:
            print("Ein Fehler ist aufgetreten, die Seite der Checkbox konnte nicht aus der checkbox_id heraus ermittelt werden. Exception: ", e)
            return None
        page_data = session['CHECK_BOXES'][str(page_number)]
        if checkbox_id in page_data:
            return page_data[checkbox_id]
        return None



##########Redis <-> Code: Textfelder Speichern Laden
#Speichern
def redis_save_text_field(value, text_field_id, page_number=None, session_id=None):
    global session_zwischenspeicher #daraus wird die session_id notfalls gezogen
    #print("redis_save_text_field: 1. Aufruf Funktion: ", " - value: ", value, " - text_field_id: ", text_field_id, "page_number: ", 
    #      page_number, " - Session-ID: ", session_id)
    if 'session_id' not in session and session_id is None:
        print("Redis_save_text_field: Fehler: Session-ID nicht in Session")
        return
    if session_id == None:
        if 'session_id' in session:
            session_id = session['session_id']
        elif 'session_id' in session_zwischenspeicher: #Ich muss leider ueber den Zwischenspeicher arbeiten, weil flask_session nur waehrend ein Link aufgerufen wird, speichert
            session_id = session_zwischenspeicher['session_id']
        else:
            session_id = None
    if page_number is None:
        try:
            page_matching = re.search(r'-(\d+)-', text_field_id)
            page_number = int(page_matching.group(1)) if page_matching else None
        except Exception as e:
            print("redis_save_text_field: Ein Fehler ist aufgetreten, die Seite des Textfeldes konnte nicht aus der textfield_id heraus ermittelt werden. Exception: ", e)
            return None
    #print("redis_save_text_field: KEYERMITTLUNG key in dem gespeichert wird: ", "- value: ", value, "- text_field_id: ", text_field_id)
    redis_key = f'session:{session_id}:page:{page_number}:text_field_id:'
    #print("redis_save_text_field: KEYERMITTLUNG key in dem gespeichert wird: ", "- value: ", value, "- text_field_id: ", text_field_id)
    try:
        # Speichere den Wert in Redis
        redis_client.hset(redis_key, str(text_field_id), str(value))
        # Setze eine Ablaufzeit von 480 Stunden
        redis_client.expire(redis_key, timedelta(hours=480))
        #print(f"redis_save_text_field: Erfolg: Wert - {value} - korrekt gespeichert unter {redis_key}")
        return
    except Exception as e:
        print(f"redis_save_text_field: Fehler: ist aufgetreten. Folgende Exception: {e}")
        return

#Laden
def redis_load_text_field(text_field_id, page_number=None, session_id=None):
    try:
        if session_id == None and 'session_id' in session:
            session_id = session['session_id']
        elif session_id == None and 'session_id' in session_zwischenspeicher:
            try:
                session_id = session_zwischenspeicher['session_id']
            except Exception as e:
                print("redis_load_text_field: Ein Fehler ist beim Versuch des Ziehens der session_id passiert. Exception: ", e)
        else:
            print("redis_load_text_field: Ein Fehler ist beim Versuch des Ziehens der session_id passiert. Exception: ", e)
            return None
        #print(f"redis_load_text_field: session_id wurde erfolgreich geladen {session_id}")
        if page_number == None:
            try:
                page_matching = re.search(r'-(\d+)-', text_field_id)
                page_number = int(page_matching.group(1)) if page_matching else None
            except Exception as e:
                #print("redis_load_text_field: Ein Fehler ist aufgetreten, die Seite des Textfeldes konnte nicht aus der textfield_id heraus ermittelt werden. Exception: ", e)
                return None
        if text_field_id != None:
            redis_key = f'session:{session_id}:page:{page_number}:text_field_id:'
            #print("redis_load_text_field: redis_key erfolgreich geladen: ", redis_key)
            # Lade Daten aus Redis
            text_data = redis_client.hgetall(redis_key)
            #print("redis_load_text_field: text_data erfolgreich geladen: ", text_data)
            if text_data:
                text_data = {k.decode('utf-8'): v.decode('utf-8') for k, v in text_data.items()}
            else:
                return None
            value = text_data[text_field_id] if text_data[text_field_id] else None
            #print("redis_load_text_field: value erfolgreich geladen: ", value)
            return value
    except Exception as e:
        print("redis_load_text_field: Error: Es wurde versucht, aus dem Redis zu laden und ein Fehler ist aufgetreten. Folgender Fehler: ", e)
        return None


########## Redis <-> Code: Checkboxen Speichern Laden
# Speichern
def redis_save_checkbox(value, check_box_id, page_number=None, session_id=None):
    if 'session_id' not in session and session_id is None:
        print("Redis_save_checkbox: Fehler: Session-ID nicht in Session")
        return

    if session_id is None and 'session_id' in session:
        session_id = session['session_id']
    elif 'session_id' in session_zwischenspeicher:
        session_id = session_zwischenspeicher['session_id']
    else:
        session_id = None
    if page_number is None:
        try:
            page_matching = re.search(r'-(\d+)-', check_box_id)
            page_number = int(page_matching.group(1)) if page_matching else None
        except Exception as e:
            #print("redis_save_checkbox: Ein Fehler ist aufgetreten, die Seite der Checkbox konnte nicht aus der check_box_id heraus ermittelt werden. Exception: ", e)
            return None

    redis_key = f'session:{session_id}:page:{page_number}:check_box_id:'
    try:
        # Speichere den Wert in Redis (als String, um boolesche Werte zu erhalten)
        redis_client.hset(redis_key, str(check_box_id), str(value))
        # Setze eine Ablaufzeit von 24 Stunden
        redis_client.expire(redis_key, timedelta(hours=480))
        #print(f"redis_save_checkbox: Erfolg: Wert - {value} - korrekt gespeichert unter {redis_key}")
        return
    except Exception as e:
        #print(f"redis_save_checkbox: Fehler: ist aufgetreten. Folgende Exception: {e}")
        return

# Laden
def redis_load_checkbox(check_box_id, page_number=None, session_id=None):
    try:
        if session_id == None and 'session_id' in session:
            try:
                session_id = session['session_id']
            except Exception as e:
                #print("redis_load_checkbox: Ein Fehler ist beim Versuch des Ziehens der session_id passiert. Exception: ", e)
                return None
        elif session_id == None and 'session_id' in session_zwischenspeicher:
            session_id = session_zwischenspeicher['session_id']
        else:
            print("redis_load_checkbox: Fataler Fehler - die session_id wurde weder in der Session noch im Zwischenspeicher gefunden.")
        if page_number == None:
            try:
                page_matching = re.search(r'-(\d+)-', check_box_id)
                page_number = int(page_matching.group(1)) if page_matching else None
            except Exception as e:
                #print("redis_load_checkbox: Ein Fehler ist aufgetreten, die Seite der Checkbox konnte nicht aus der check_box_id heraus ermittelt werden. Exception: ", e)
                return None

        redis_key = f'session:{session_id}:page:{page_number}:check_box_id:'
        # Lade Daten aus Redis
        checkbox_data = redis_client.hgetall(redis_key)
        if checkbox_data:
            checkbox_data = {k.decode('utf-8'): v.decode('utf-8') for k, v in checkbox_data.items()}
        else:
            return None
        # Konvertiere den Wert zu einem booleschen Wert
        stored_value = checkbox_data.get(check_box_id)
        if stored_value is not None:
            return stored_value.lower() == 'true' # Konvertiere den String zu einem booleschen Wert
        return None
    except Exception as e:
        #print("Error: Es wurde versucht, aus dem Redis zu laden und ein Fehler ist aufgetreten. Folgender Fehler: ", e)
        return None


########## Redis <-> Session Synchronisation: Textfelder gleichzeitig in Redis und in der Session speichern
def wrapped_save_text_field(value, text_field_id, page_number=None, session_id=None):
    #print("wrapped_save_text_field (1.): text_field_id: ",text_field_id, ", - value: ", value, ", - Typ des Value: ", type(value), "page_number: ", page_number, "session-id: ", session_id)
    #print("wrapped_save_text_field (2.): value!!!: ", value)
    if session_id == None:# and 'session_id' in session:
        session_id = session_zwischenspeicher['session_id']
    #print("wrapped_save_text_field (3.): session_id: ", session_id)
    if page_number == None:
        try:
            page_matching = re.search(r'-(\d+)-', text_field_id)
            page_number = int(page_matching.group(1)) if page_matching else None
        except Exception as e:
            #print("wrapped_save_text_field: Ein Fehler ist aufgetreten, die Seite der Checkbox konnte nicht aus der checkbox_id heraus ermittelt werden. Exception: ", e)
            return None
    try:
        session_save_text_field(value, text_field_id, page_number)
        redis_save_text_field(value, text_field_id, page_number, session_id)

    except Exception as e:
        #print(f"wrapped_save_text_field: Das Textfeld {text_field_id} konnte nicht gespeichert werden. Der Fehler ist folgender: ", e)
        return
    print(f"wrapped_save_text_field: Das Textfeld {text_field_id} wurde erfolgreich in der Session und in Redis gespeichert mit Value {value}.")

########## Redis <-> Session Synchronisation: Textfelder gleichzeitig in Redis und in der Session speichern
def wrapped_save_checkbox(value, check_box_id, page_number=None, session_id=None):
    if session_id == None:
        session_id = session_zwischenspeicher['session_id']
    if page_number == None:
        try:
            page_matching = re.search(r'-(\d+)-', check_box_id)
            page_number = int(page_matching.group(1)) if page_matching else None
        except Exception as e:
            #print("wrapped_save_text_field: Ein Fehler ist aufgetreten, die Seite der Checkbox konnte nicht aus der checkbox_id heraus ermittelt werden. Exception: ", e)
            return None
    try:
        session_save_checkbox(value, check_box_id, page_number)
        redis_save_checkbox(value, check_box_id, page_number, session_id)

    except Exception as e:
        #print(f"wrapped_save_checkbox: Das Textfeld {check_box_id} konnte nicht gespeichert werden. Der Fehler ist folgender: ", e)
        return
    #print(f"wrapped_save_checkbox: Das Textfeld {check_box_id} wurde erfolgreich in der Session und in Redis gespeichert.")


########## Redis <-> Session Synchronisation: 
@flask_app.before_request
def update_session_text_fields_from_global_session_zwischenspeicher():
    if 'TEXT_FIELDS' in session_zwischenspeicher:
        session['TEXT_FIELDS'] = session_zwischenspeicher['TEXT_FIELDS']
        #session_zwischenspeicher['TEXT_FIELDS'] = 
    else:
        print()

@flask_app.before_request
def update_session_checkboxes_from_global_session_zwischenspeicher():
    if 'CHECK_BOXES' in session_zwischenspeicher:
        session['CHECK_BOXES'] = session_zwischenspeicher['CHECK_BOXES']
        #session_zwischenspeicher['TEXT_FIELDS'] = 
    else:
        print()


##### Routen: Um die Daten aus Flask rauszubekommen oder Werte in Flask zu speichern
#Nimmt ein dict an keys und Values an, die alle geupdatet werden sollen und updatet sie.
@flask_app.route('/save_text_fields', methods=['POST'])
def save_text_fields():
    data = request.json
    dict_ids_values = data.get('dict_ids_values')
    #print("save_text_fields: DICT_IDS_VALUES: ", dict_ids_values)
    
    try:
        for textfield_id, value in dict_ids_values.items():
            wrapped_save_text_field(value, textfield_id)
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400
    return jsonify({"status": "success", "message": f"Textfelder erfolgreich gespeichert. Gespeicherte Textfelder {dict_ids_values}"})

@flask_app.route('/save_checkboxes', methods=['POST'])
def save_checkboxes():
    data = request.json
    dict_ids_values = data.get('dict_ids_values')
    
    try:
        for checkbox_id, value in dict_ids_values.items():
            print(f"save_checkboxes (flask-route): Checkbox-ID: {checkbox_id}, Value {value}")
            checkbox_value = True if value == ["checked"] else False
            wrapped_save_checkbox(checkbox_value, checkbox_id)########################### GANZ DICKER FEHLER
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400
    return jsonify({"status": "success", "message": f"Checkboxen erfolgreich gespeichert. Gespeicherte Checkboxen {dict_ids_values}"})

#Zweckloesung: Die Daten werden in einem Zwischenspeicher gelagert
@flask_app.before_request
def update_session_zwischenspeicher():
    global session_zwischenspeicher
    session_zwischenspeicher['session_id'] = session['session_id'] if 'session_id' in session else session_zwischenspeicher['session_id']
    session_zwischenspeicher['current_page'] = session['current_page'] if 'current_page' in session else session_zwischenspeicher['current_page']
    session_zwischenspeicher['current_url'] = session['current_url'] if 'current_url' in session else session_zwischenspeicher['current_url']
    session_zwischenspeicher['TEXT_FIELDS'] = session['TEXT_FIELDS'] if 'TEXT_FIELDS' in session else session_zwischenspeicher['TEXT_FIELDS']
    session_zwischenspeicher['CHECK_BOXES'] = session['CHECK_BOXES'] if 'CHECK_BOXES' in session else session_zwischenspeicher['CHECK_BOXES']
    session_zwischenspeicher['initialized'] = session['initialized'] if 'initialized' in session else session_zwischenspeicher['initialized']

@flask_app.before_request
def send_textfields_to_dash_automatisch_mit_jedem_Request():
    global flasksocketio_hostsocket
    global session_zwischenspeicher
    print("HOSTSOCKET - Daten werden gesendet.")
    try:
        TEXTFIELDS = session_zwischenspeicher["TEXT_FIELDS"] if "TEXT_FIELDS" in session_zwischenspeicher else None
        print(f"ZU EMITTENDE DATEN (send_textfields_to_dash_automatisch_mit_jedem_Request): {TEXTFIELDS}")
        flasksocketio_hostsocket.emit('textfields_to_dash', TEXTFIELDS)
        print(f"flasksocketio_hostsocket: EMIT WURDE VORGENOMMEN mit folgenden Textfield-Daten: {TEXTFIELDS}")
    except Exception as e:
        print("HOSTSOCKET: Folgender Fehler ist aufgetreten: ", e)

@flask_app.before_request
def send_checkboxes_to_dash_automatisch_mit_jedem_Request():
    global flasksocketio_hostsocket
    global session_zwischenspeicher
    print("HOSTSOCKET - Daten werden gesendet.")
    try:
        CHECK_BOXES = session_zwischenspeicher["CHECK_BOXES"] if "CHECK_BOXES" in session_zwischenspeicher else None
        print(f"ZU EMITTENDE DATEN (send_checkboxes_to_dash_automatisch_mit_jedem_Request): {CHECK_BOXES}")
        flasksocketio_hostsocket.emit('checkboxes_to_dash', CHECK_BOXES)
        print(f"flasksocketio_hostsocket: EMIT WURDE VORGENOMMEN mit folgenden Checkbox-Daten: {CHECK_BOXES}")
    except Exception as e:
        print("HOSTSOCKET: Folgender Fehler ist aufgetreten: ", e)

def send_textfields_to_dash():
    global flasksocketio_hostsocket
    global session_zwischenspeicher
    print("HOSTSOCKET - Daten werden gesendet.")
    try:
        TEXTFIELDS = session_zwischenspeicher["TEXT_FIELDS"] if "TEXT_FIELDS" in session_zwischenspeicher else None
        print(f"ZU EMITTENDE DATEN (send_textfields_to_dash): {TEXTFIELDS}")
        flasksocketio_hostsocket.emit('textfields_to_dash', TEXTFIELDS)
        print(f"flasksocketio_hostsocket: EMIT WURDE VORGENOMMEN mit folgenden Textfield-Daten: {TEXTFIELDS}")
    except Exception as e:
        print("HOSTSOCKET: Folgender Fehler ist aufgetreten: ", e)

def send_checkboxes_to_dash():
    global flasksocketio_hostsocket
    global session_zwischenspeicher
    print("HOSTSOCKET - Daten werden gesendet.")
    try:
        CHECK_BOXES = session_zwischenspeicher["CHECK_BOXES"] if "CHECK_BOXES" in session_zwischenspeicher else None
        print("ZU EMITTENDE DATEN (send_checkboxes_to_dash): ", CHECK_BOXES)
        flasksocketio_hostsocket.emit('checkboxes_to_dash', CHECK_BOXES)
        print(f"flasksocketio_hostsocket: EMIT WURDE VORGENOMMEN mit folgenden Checkbox-Daten: {CHECK_BOXES}")
    except Exception as e:
        print("HOSTSOCKET: Folgender Fehler ist aufgetreten: ", e)

def send_session_id_to_dash(session_id = None):
    global flasksocketio_hostsocket
    global session_zwischenspeicher
    print("HOSTSOCKET - Daten werden gesendet.")
    try:
        SESSION_ID = session_zwischenspeicher["session_id"] if "session_id" in session_zwischenspeicher else None
        print(f"ZU EMITTENDE DATEN (send_session_id_to_dash): {SESSION_ID}")
        flasksocketio_hostsocket.emit('session_id_to_dash', SESSION_ID)
        print("EMITTETE DATEN aus send_session_id_to_dash: ", SESSION_ID)
        print(f"flasksocketio_hostsocket: EMIT WURDE VORGENOMMEN mit folgenden Session-ID-Daten: {SESSION_ID}")
    except Exception as e:
        print("HOSTSOCKET: Folgender Fehler ist aufgetreten: ", e)

##### Route: Um zum Dash-Port auf die entsprechende Dash-Seite zu leiten
#Requeste z.B. /redirect_dash/50 und es leitet zu localhost:8050/50 weiter, also Seite 50 der Dash-App
@flask_app.route('/redirect_dash/<int:page_number>')
def redirect_dash(page_number):
    return redirect(f"{host_ip}:{dash_port}/{page_number}")

'''
#Session_ID erhalten. Was man aufrufen muss: die get_session_id()
@flask_app.route('/get_session_id_', methods=['GET'])
def get_session_id_():
    if session:
        print(f"get_session_id_: Session - 'session_id': ", session['session_id'] if 'session_id' in session else 'KEINE SESSION-ID DRIN SCHEISE ABER AUCH')
        return session['session_id'] if 'session_id' in session else 'KEINE SESSION-ID DRIN SCHEISE ABER AUCH'
    else:
        return "Keine session gefunden", 404

def get_session_id():
    response = requests.get("http://127.0.0.1:5000/get_session_id_")
    return response.text if response.status_code == 200 else None'''




##### Debugging in der Main Methode
def periodic_session_check():
    while True:
        global flasksocketio_hostsocket
        global session_zwischenspeicher
        print("HOSTSOCKET - Daten werden gesendet.")
        try:
            TEXTFIELDS = session_zwischenspeicher["TEXT_FIELDS"] if "TEXT_FIELDS" in session_zwischenspeicher else None
            print("ZU EMITTENDE DATEN (period_session_check): ", TEXTFIELDS)
            flasksocketio_hostsocket.emit('textfields_to_dash', TEXTFIELDS)
            print("flasksocketio_hostsocket: EMIT WURDE VORGENOMMEN")
        except Exception as e:
            print("HOSTSOCKET: Folgender Fehler ist aufgetreten: ", e)
        #print(f"periodic_session_check: Aktuelle Session ID: {session_id}")
        time.sleep(0.5)  # Wartet 500ms'''


##########Flask App Ausfuehrung und Dash App Ausfuehrung
#####Startet Flask und Flask-SocketIO (dann in einem separaten Thread)
def run_flask_socket():
    #print("Flask und Socket werden gestartet.")
    flask_app.run(port=5000, debug=True, use_reloader=False)
    time.sleep(2)
    print("Flask und Socket wurden gestartet.")
    
if __name__ == '__main__':
    #session_check_thread = threading.Thread(target=periodic_session_check)
    #session_check_thread.daemon = True  # Beendet den Thread, wenn das Hauptprogramm endet
    #session_check_thread.start()
    flasksocketio_hostsocket.run(flask_app, debug=True, port=5000)
    run_flask_socket()
