
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
import sqlite3, json, threading, datetime, hashlib, io
from pathlib import Path

# ── Import engine ──────────────────────────────────────────────────
import sys
sys.path.insert(0, str(Path(__file__).parent))
from engine import (init_db, get_cfg, set_cfg, get_db, ENG, PROLOG,
                    DB, KB, BG0,BG1,BG2,BG3,BORD,TX,TX2,TX3,
                    AMB,AMB2,AMB3,GRN,GRN2,RED,RED2,YEL,WHT,
                    FB,FSM,FM,FM2,FBTN,FBIG,FT,FTB)

def mk_btn(p,txt,cmd,accent=False,danger=False,**kw):
    bg=AMB if accent else (RED2 if danger else BG3)
    fg=BG0 if accent else TX2
    ab=AMB2 if accent else (RED if danger else BG3)
    return tk.Button(p,text=txt,command=cmd,bg=bg,fg=fg,
                     activebackground=ab,activeforeground=fg,
                     relief="flat",font=FBTN,cursor="hand2",
                     padx=10,pady=5,bd=0,**kw)

def mk_entry(p,**kw):
    return tk.Entry(p,bg=BG2,fg=TX,insertbackground=AMB,
                    relief="flat",font=FB,
                    highlightthickness=1,highlightbackground=BORD,
                    highlightcolor=AMB3,**kw)

def mk_lbl(p,txt,fg=None,bg=None,**kw):
    return tk.Label(p,text=txt,fg=fg or TX2,bg=bg or BG1,font=FB,**kw)

def mk_sep(p,bg=None):
    return tk.Frame(p,bg=bg or BORD,height=1)

def mk_chk(p,var,txt):
    c = tk.Checkbutton(p,variable=var,text=txt,bg=BG2,fg=TX2,
        selectcolor=BG0,activebackground=BG3,activeforeground=AMB,
        font=FB,relief="flat")
    c.bind("<Enter>",lambda e:c.config(fg=AMB))
    c.bind("<Leave>",lambda e:c.config(fg=AMB2 if var.get() else TX2))
    return c

def export_pdf(case_data, save_path):
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.lib.styles import ParagraphStyle
        from reportlab.lib.units import inch
        from reportlab.lib import colors
        from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,Table,TableStyle,HRFlowable
        from reportlab.lib.enums import TA_CENTER
    except ImportError:
        return False,"Install reportlab: pip install reportlab"

    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf,pagesize=letter,
        leftMargin=.75*inch,rightMargin=.75*inch,
        topMargin=.75*inch,bottomMargin=.75*inch)

    judge=get_cfg("judge","Hon. System Judge"); court=get_cfg("court","AI Reasoning Court")
    verdict=case_data.get("verdict","unknown")

    def ps(n,**kw): return ParagraphStyle(n,**kw)
    ts  = ps("T",fontSize=17,fontName="Helvetica-Bold",alignment=TA_CENTER,spaceAfter=3)
    ss  = ps("S",fontSize=9,fontName="Helvetica",alignment=TA_CENTER,spaceAfter=2,textColor=colors.grey)
    h1s = ps("H",fontSize=11,fontName="Helvetica-Bold",spaceBefore=12,spaceAfter=5,
             textColor=colors.HexColor("#1c2033"))
    bs  = ps("B",fontSize=8,fontName="Helvetica",spaceAfter=3,leading=13)
    ms  = ps("M",fontSize=7,fontName="Courier",spaceAfter=2,leading=11,
             textColor=colors.HexColor("#444"))
    vs  = ps("V",fontSize=14,fontName="Helvetica-Bold",alignment=TA_CENTER,textColor=colors.white)

    vc = colors.HexColor("#1f5c38") if verdict=="granted" else \
         colors.HexColor("#7a5a1a") if verdict=="surety"  else \
         colors.HexColor("#7a2020")
    vt_txt = {"granted":"  GRANTED","surety":"  GRANTED WITH SURETY","denied":"  DENIED"}.get(verdict,"INCONCLUSIVE")

    story=[]
    story.append(Paragraph(court,ss))
    story.append(Paragraph("LEGAL REASONING SYSTEM — CASE REPORT",ts))
    story.append(Paragraph(
        f"Case ID: {case_data.get('case_id','—')}   |   {datetime.datetime.now().strftime('%d %b %Y, %H:%M')}",ss))
    story.append(HRFlowable(width="100%",thickness=2,color=colors.HexColor("#b8975a"),spaceAfter=10))
    vt=Table([[Paragraph(vt_txt,vs)]],colWidths=[6.9*inch])
    vt.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,-1),vc),
        ("TOPPADDING",(0,0),(-1,-1),12),("BOTTOMPADDING",(0,0),(-1,-1),12)]))
    story.append(vt); story.append(Spacer(1,10))
    story.append(Paragraph("CASE INFORMATION",h1s))
    info=[["Subject",case_data.get("subject","—"),"Module",case_data.get("module","—").title()],
          ["Rule",case_data.get("rule","—"),"Engine",case_data.get("engine","—")],
          ["Reason",case_data.get("reason","—"),"Date",str(case_data.get("created_at","—"))[:16]]]
    it=Table(info,colWidths=[1.1*inch,2.2*inch,1.1*inch,2.5*inch])
    it.setStyle(TableStyle([
        ("FONTNAME",(0,0),(0,-1),"Helvetica-Bold"),("FONTNAME",(2,0),(2,-1),"Helvetica-Bold"),
        ("FONTSIZE",(0,0),(-1,-1),7.5),
        ("GRID",(0,0),(-1,-1),0.4,colors.HexColor("#dddddd")),
        ("ROWBACKGROUNDS",(0,0),(-1,-1),[colors.white,colors.HexColor("#f8f8f8")]),
        ("TOPPADDING",(0,0),(-1,-1),4),("BOTTOMPADDING",(0,0),(-1,-1),4),
        ("LEFTPADDING",(0,0),(-1,-1),6)]))
    story.append(it); story.append(Spacer(1,8))
    story.append(Paragraph("KNOWLEDGE BASE FACTS",h1s))
    facts=json.loads(case_data.get("facts","{}"))
    fd=[[k.replace("_"," ").title(),str(v)] for k,v in facts.items()]
    if fd:
        ft=Table(fd,colWidths=[3.45*inch,3.45*inch])
        ft.setStyle(TableStyle([
            ("FONTSIZE",(0,0),(-1,-1),7.5),("FONTNAME",(0,0),(0,-1),"Helvetica-Bold"),
            ("GRID",(0,0),(-1,-1),0.4,colors.HexColor("#dddddd")),
            ("ROWBACKGROUNDS",(0,0),(-1,-1),[colors.white,colors.HexColor("#f8f8f8")]),
            ("TOPPADDING",(0,0),(-1,-1),3),("BOTTOMPADDING",(0,0),(-1,-1),3),
            ("LEFTPADDING",(0,0),(-1,-1),6)]))
        story.append(ft); story.append(Spacer(1,8))
    story.append(Paragraph("INFERENCE TRACE — SLD Resolution",h1s))
    trace=json.loads(case_data.get("trace","[]"))
    syms={"pass":"[PASS]","fail":"[FAIL]","rule":"[RULE]","info":"[INFO]","warn":"[WARN]"}
    clrs={"pass":"#1f5c38","fail":"#7a2020","rule":"#1c2033","info":"#555","warn":"#7a5a1a"}
    for i,step in enumerate(trace):
        st=step.get("s","info"); sym=syms.get(st,"[    ]"); cl=clrs.get(st,"#333")
        story.append(Paragraph(
            f'<font color="{cl}"><b>{i+1:02d}. {sym}</b> {step.get("p","")}</font>',bs))
        story.append(Paragraph(
            f'<font color="#888">&nbsp;&nbsp;&nbsp;&nbsp;{step.get("l","")}</font>',ms))
    if case_data.get("notes","").strip():
        story.append(Spacer(1,8)); story.append(Paragraph("NOTES",h1s))
        story.append(Paragraph(case_data["notes"],bs))
    story.append(Spacer(1,12))
    story.append(HRFlowable(width="100%",thickness=0.5,color=colors.lightgrey,spaceAfter=4))
    story.append(Paragraph(f"Presiding: {judge}   |   LexLogic Desktop v2.0",ss))
    doc.build(story)
    with open(save_path,"wb") as f: f.write(buf.getvalue())
    return True, save_path
