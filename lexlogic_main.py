import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
import sqlite3, json, threading, datetime, hashlib, io, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from engine import (init_db,get_cfg,set_cfg,get_db,ENG,PROLOG,DB,KB,
    BG0,BG1,BG2,BG3,BORD,TX,TX2,TX3,AMB,AMB2,AMB3,
    GRN,GRN2,RED,RED2,YEL,WHT,FB,FSM,FM,FM2,FBTN,FBIG,FT,FTB)
from utils import mk_btn,mk_entry,mk_lbl,mk_sep,mk_chk,export_pdf
