import threading, shutil, subprocess, re
from pathlib import Path
from tkinter import filedialog
import customtkinter as ctk
from PIL import Image
import yt_dlp, requests
from io import BytesIO

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

BG = "#08080a"
CARD = "#121214"
SURFACE = "#1c1c1f"
SURFACE2 = "#252529"
BORDER = "#232326"
TEXT = "#ffffff"
MUTED = "#8b8b93"
DIM = "#52525b"
ACCENT = "#ff3355"
ACCENT_H = "#e6294a"
ACCENT2 = "#7c5cff"
ACCENT2_H = "#6a4de6"

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("AuraFetch — YouTube to MP3 / MP4")
        self.geometry("900x700")
        self.minsize(720, 520)
        self.configure(fg_color=BG)
        self.info=None
        self.thumb=None
        self.folder=str(Path.home()/"Downloads")
        self.grid_columnconfigure(0,weight=1)
        self.grid_rowconfigure(1,weight=1)
        self._build()
        self.after(150,self._check_ffmpeg)
        self.bind("<Control-v>",lambda e:self._paste())
        self.bind("<Control-V>",lambda e:self._paste())

    def _build(self):
        top=ctk.CTkFrame(self,fg_color=BG,height=64)
        top.grid(row=0,column=0,sticky="ew",padx=28,pady=(18,0))
        top.grid_columnconfigure(1,weight=1)
        left=ctk.CTkFrame(top,fg_color="transparent")
        left.grid(row=0,column=0,sticky="w")
        ctk.CTkLabel(left,text="⬢",font=("Segoe UI",26),text_color=ACCENT).pack(side="left",padx=(0,10))
        ctk.CTkLabel(left,text="AuraFetch",font=("Segoe UI Semibold",20),text_color=TEXT).pack(side="left")
        pill=ctk.CTkLabel(left,text="  PRO  ",font=("Segoe UI Bold",9),text_color="white",fg_color=SURFACE2,corner_radius=6)
        pill.pack(side="left",padx=(10,0),pady=(2,0))
        ctk.CTkLabel(left,text="Free  •  No ads  •  No limits",font=("Segoe UI",11),text_color=DIM).pack(side="left",padx=(14,0))

        right=ctk.CTkFrame(top,fg_color="transparent")
        right.grid(row=0,column=2,sticky="e")
        self.ffmpeg_dot=ctk.CTkLabel(right,text="● ffmpeg",font=("Segoe UI",11),text_color=DIM)
        self.ffmpeg_dot.pack(side="left",padx=(0,12))
        ctk.CTkLabel(right,text="v1.1",font=("Segoe UI",11),text_color=DIM).pack(side="left")
        ctk.CTkButton(right,text="♥ Support",width=86,height=28,corner_radius=20,fg_color=SURFACE,hover_color=SURFACE2,text_color=MUTED,font=("Segoe UI",11),
                      command=lambda:__import__("webbrowser").open("https://github.com")).pack(side="left",padx=(12,0))

        self.scroll=ctk.CTkScrollableFrame(self,fg_color=BG,corner_radius=0,border_width=0,
                                             scrollbar_button_color=SURFACE2,scrollbar_button_hover_color="#323238")
        self.scroll.grid(row=1,column=0,sticky="nsew",padx=0,pady=0)
        self.scroll.grid_columnconfigure(0,weight=1)

        card=ctk.CTkFrame(self.scroll,fg_color=CARD,corner_radius=22,border_width=1,border_color=BORDER)
        card.grid(row=0,column=0,sticky="nsew",padx=28,pady=16)
        card.grid_columnconfigure(0,weight=1)

        url_wrap=ctk.CTkFrame(card,fg_color=SURFACE,corner_radius=16,border_width=1,border_color=BORDER)
        url_wrap.grid(row=0,column=0,sticky="ew",padx=20,pady=(20,14))
        url_wrap.grid_columnconfigure(0,weight=1)
        self.url=ctk.CTkEntry(url_wrap,placeholder_text="Paste YouTube link  —  video, Short or playlist",height=50,corner_radius=12,
                              fg_color=SURFACE,border_width=0,font=("Segoe UI",13),text_color=TEXT,placeholder_text_color="#5a5a62")
        self.url.grid(row=0,column=0,sticky="ew",padx=(14,6),pady=8)
        self.url.bind("<Return>",lambda e:self.fetch())
        self.url.bind("<<Paste>>",lambda e:self.after(60,self.fetch))
        ctk.CTkButton(url_wrap,text="Paste",width=68,height=36,corner_radius=10,fg_color=SURFACE2,hover_color="#2e2e33",text_color=MUTED,command=self._paste).grid(row=0,column=1,padx=4,pady=8)
        self.fetch_btn=ctk.CTkButton(url_wrap,text="Fetch",width=104,height=36,corner_radius=10,fg_color=ACCENT,hover_color=ACCENT_H,font=("Segoe UI Semibold",13),command=self.fetch)
        self.fetch_btn.grid(row=0,column=2,padx=(4,12),pady=8)

        prev=ctk.CTkFrame(card,fg_color=SURFACE,corner_radius=16,border_width=1,border_color=BORDER)
        prev.grid(row=1,column=0,sticky="ew",padx=20,pady=(0,14))
        prev.grid_columnconfigure(1,weight=1)
        self.thumb_label=ctk.CTkLabel(prev,text="◯\n\nDrop a link to preview",width=260,height=146,corner_radius=12,fg_color="#0f0f12",
                                      font=("Segoe UI",11),text_color=DIM,justify="center")
        self.thumb_label.grid(row=0,column=0,padx=14,pady=14,sticky="n")
        self.badge=ctk.CTkLabel(prev,text="",font=("Segoe UI Bold",11),text_color="white",fg_color="black",corner_radius=6)
        meta=ctk.CTkFrame(prev,fg_color="transparent")
        meta.grid(row=0,column=1,sticky="nsew",padx=(6,16),pady=14)
        self.title_l=ctk.CTkLabel(meta,text="Ready to download",font=("Segoe UI Semibold",15),text_color=TEXT,wraplength=480,anchor="w",justify="left")
        self.title_l.pack(anchor="w",fill="x")
        self.chan_l=ctk.CTkLabel(meta,text="Supports 4K / 1080p / 720p  •  MP3 320kbps  •  Playlists & Shorts",font=("Segoe UI",11),text_color=MUTED,anchor="w",wraplength=480,justify="left")
        self.chan_l.pack(anchor="w",pady=(6,0),fill="x")
        pills=ctk.CTkFrame(meta,fg_color="transparent")
        pills.pack(anchor="w",pady=(12,0),fill="x")
        self.pill_dur=self._pill(pills,"⏱  --:--")
        self.pill_views=self._pill(pills,"👁  —")
        self.pill_date=self._pill(pills,"📅  —")
        for p in (self.pill_dur,self.pill_views,self.pill_date): p.pack(side="left",padx=(0,8))

        ctrl=ctk.CTkFrame(card,fg_color="transparent")
        ctrl.grid(row=2,column=0,sticky="ew",padx=20,pady=(0,6))
        ctrl.grid_columnconfigure((0,1,2),weight=1)

        self.fmt_var=ctk.StringVar(value="MP3")
        f1=self._ctrl_box(ctrl,"FORMAT")
        f1.grid(row=0,column=0,sticky="nsew",padx=(0,6))
        self.seg=ctk.CTkSegmentedButton(f1,values=["MP3","MP4"],variable=self.fmt_var,selected_color=ACCENT,selected_hover_color=ACCENT_H,
                                        unselected_color=SURFACE2,unselected_hover_color="#2e2e33",font=("Segoe UI Semibold",12),height=36,corner_radius=10,command=self._on_fmt)
        self.seg.pack(fill="x",padx=12,pady=(2,12))

        f2=self._ctrl_box(ctrl,"QUALITY")
        f2.grid(row=0,column=1,sticky="nsew",padx=6)
        self.qual_var=ctk.StringVar(value="320 kbps")
        self.qual_menu=ctk.CTkOptionMenu(f2,variable=self.qual_var,values=["320 kbps","256 kbps","192 kbps","128 kbps"],
                                         fg_color=SURFACE,button_color=SURFACE2,button_hover_color="#33333a",dropdown_fg_color=SURFACE,text_color=TEXT,font=("Segoe UI",12),height=36,corner_radius=10)
        self.qual_menu.pack(fill="x",padx=12,pady=(2,12))
        self.qual_menu.bind("<Button-1>",lambda e:None)

        f3=self._ctrl_box(ctrl,"SAVE TO")
        f3.grid(row=0,column=2,sticky="nsew",padx=(6,0))
        row=ctk.CTkFrame(f3,fg_color="transparent")
        row.pack(fill="x",padx=12,pady=(2,12))
        row.grid_columnconfigure(0,weight=1)
        self.folder_l=ctk.CTkLabel(row,text=self._short(self.folder),font=("Segoe UI",11),text_color=MUTED,anchor="w")
        self.folder_l.grid(row=0,column=0,sticky="w")
        ctk.CTkButton(row,text="↗",width=36,height=32,corner_radius=8,fg_color=SURFACE2,hover_color="#33333a",command=self._pick).grid(row=0,column=1,padx=(8,0))

        opts=ctk.CTkFrame(card,fg_color="transparent")
        opts.grid(row=3,column=0,sticky="ew",padx=20,pady=(8,0))
        self.playlist_var=ctk.BooleanVar(value=False)
        ctk.CTkSwitch(opts,text="Entire playlist",variable=self.playlist_var,progress_color=ACCENT,fg_color=SURFACE2,font=("Segoe UI",12),text_color=MUTED).pack(side="left")
        ctk.CTkLabel(opts,text="·",text_color=DIM,font=("Segoe UI",14)).pack(side="left",padx=10)
        self.split_var=ctk.BooleanVar(value=False)
        ctk.CTkSwitch(opts,text="Split chapters",variable=self.split_var,progress_color=ACCENT,fg_color=SURFACE2,font=("Segoe UI",12),text_color=MUTED).pack(side="left")
        self.status=ctk.CTkLabel(opts,text="Idle",font=("Segoe UI",11),text_color=DIM)
        self.status.pack(side="right")

        prog_wrap=ctk.CTkFrame(card,fg_color="transparent")
        prog_wrap.grid(row=4,column=0,sticky="ew",padx=20,pady=(14,4))
        prog_wrap.grid_columnconfigure(0,weight=1)
        ctk.CTkLabel(prog_wrap,text="PROGRESS",font=("Segoe UI",9),text_color=DIM).grid(row=0,column=0,sticky="w")
        self.pct_l=ctk.CTkLabel(prog_wrap,text="0%",font=("Segoe UI Bold",11),text_color=MUTED)
        self.pct_l.grid(row=0,column=1,sticky="e")
        self.bar=ctk.CTkProgressBar(prog_wrap,height=8,corner_radius=99,fg_color=SURFACE2,progress_color=ACCENT)
        self.bar.grid(row=1,column=0,columnspan=2,sticky="ew",pady=(6,0))
        self.bar.set(0)
        self.speed_l=ctk.CTkLabel(prog_wrap,text="",font=("Segoe UI",11),text_color=DIM,anchor="w")
        self.speed_l.grid(row=2,column=0,sticky="w",pady=(4,0))
        self.eta_l=ctk.CTkLabel(prog_wrap,text="",font=("Segoe UI",11),text_color=DIM,anchor="e")
        self.eta_l.grid(row=2,column=1,sticky="e",pady=(4,0))

        self.dl_btn=ctk.CTkButton(card,text="⬇  Download MP3  •  320 kbps",height=52,corner_radius=14,fg_color=ACCENT,hover_color=ACCENT_H,
                                  font=("Segoe UI Semibold",14),state="disabled",command=self._download)
        self.dl_btn.grid(row=5,column=0,sticky="ew",padx=20,pady=(14,20))
        self.fmt_var.trace_add("write",lambda *_:self._refresh_dl_text())
        self.qual_var.trace_add("write",lambda *_:self._refresh_dl_text())

        ctk.CTkLabel(self.scroll,text="Tip: Ctrl+V to paste  •  Works on Windows, macOS & Linux  •  yt-dlp powered",font=("Segoe UI",10),text_color="#3a3a40").grid(row=1,column=0,pady=(0,16))

    def _pill(self,parent,text):
        return ctk.CTkLabel(parent,text=text,font=("Segoe UI",11),text_color=MUTED,fg_color=SURFACE2,corner_radius=20,padx=10,pady=4)

    def _ctrl_box(self,parent,title):
        b=ctk.CTkFrame(parent,fg_color=SURFACE,corner_radius=14,border_width=1,border_color=BORDER)
        ctk.CTkLabel(b,text=title,font=("Segoe UI",9),text_color=DIM).pack(pady=(10,0))
        return b

    def _short(self,p,n=28): return p if len(p)<=n else "…"+p[-(n-1):]
    def _paste(self):
        try:
            t=self.clipboard_get().strip()
            self.url.delete(0,"end"); self.url.insert(0,t); self.fetch()
        except: pass
    def _pick(self):
        d=filedialog.askdirectory(initialdir=self.folder)
        if d: self.folder=d; self.folder_l.configure(text=self._short(d))
    def _on_fmt(self,v):
        if v=="MP3":
            self.qual_menu.configure(values=["320 kbps","256 kbps","192 kbps","128 kbps"]); self.qual_var.set("320 kbps")
            self.bar.configure(progress_color=ACCENT); self.seg.configure(selected_color=ACCENT,selected_hover_color=ACCENT_H)
        else:
            self.qual_menu.configure(values=["Best","1080p","720p","480p","360p"]); self.qual_var.set("Best")
            self.bar.configure(progress_color=ACCENT2); self.seg.configure(selected_color=ACCENT2,selected_hover_color=ACCENT2_H)
        self._refresh_dl_text()
    def _refresh_dl_text(self):
        f=self.fmt_var.get(); q=self.qual_var.get()
        icon="♫" if f=="MP3" else "▶"
        col=ACCENT if f=="MP3" else ACCENT2
        hov=ACCENT_H if f=="MP3" else ACCENT2_H
        self.dl_btn.configure(text=f"{icon}  Download {f}  •  {q}",fg_color=col,hover_color=hov)
    def _check_ffmpeg(self):
        ok=shutil.which("ffmpeg") is not None
        if not ok:
            try: subprocess.run(["ffmpeg","-version"],capture_output=True,timeout=2); ok=True
            except: ok=False
        self.ffmpeg_dot.configure(text="● ffmpeg ready" if ok else "● ffmpeg missing", text_color="#2ecc71" if ok else "#e67e22")
    def _set_status(self,t,c=DIM): self.status.configure(text=t,text_color=c)

    def fetch(self):
        u=self.url.get().strip()
        if not u or "youtu" not in u and "youtube" not in u:
            self._set_status("Paste a valid YouTube URL","#e74c3c"); return
        u=re.sub(r"&.*$","",u)
        self.fetch_btn.configure(state="disabled",text="…")
        self._set_status("Fetching…",MUTED)
        threading.Thread(target=self._fetch_t,args=(u,),daemon=True).start()

    def _fetch_t(self,url):
        opts={"quiet":True,"no_warnings":True,"skip_download":True,"extract_flat":"in_playlist",
              "ignoreerrors":True,"ignore_no_formats_error":True,"socket_timeout":30,"retries":3}
        try:
            with yt_dlp.YoutubeDL(opts) as ydl:
                info=ydl.extract_info(url,download=False)
                if not info:
                    raise Exception("Video unavailable (private/deleted)")
                # Playlist? find first playable entry and fetch its full metadata
                if info and "entries" in info and info["entries"]:
                    first_valid=None
                    for e in info["entries"]:
                        if e and (e.get("id") or e.get("url")):
                            # skip private/deleted placeholders
                            t=(e.get("title") or "").lower()
                            if t in ("[private video]","[deleted video]","private video","deleted video"):
                                continue
                            first_valid=e
                            break
                    if first_valid is None:
                        raise Exception("Playlist has no playable videos (all private/deleted)")
                    vid=first_valid.get("url") or first_valid.get("id")
                    # flattened entries only have id — resolve to full video URL
                    if vid and not str(vid).startswith("http"):
                        vid=f"https://www.youtube.com/watch?v={vid}"
                    # full extract for preview of that single video
                    info2=ydl.extract_info(vid,download=False)
                    if info2 and "entries" in info2 and info2["entries"]:
                        # extremely rare: resolved URL was still a playlist
                        for e in info2["entries"]:
                            if e and e.get("title") not in (None,"[Private video]","[Deleted video]"):
                                info=e
                                break
                        else:
                            info=first_valid
                    else:
                        info=info2 or first_valid
                if isinstance(info,dict) and info.get("ie_key")=="YoutubeTab":  # playlist without entries?
                    raise Exception("Playlist — enable 'Entire playlist' to fetch")
            self.info=info
            title=info.get("title","Unknown")
            chan=info.get("uploader") or info.get("channel") or "YouTube"
            dur=info.get("duration") or 0
            views=info.get("view_count") or 0
            date=(info.get("upload_date") or "")[0:4]
            m,s=divmod(int(dur),60); h,m=divmod(m,60)
            dur_s=f"{h}:{m:02d}:{s:02d}" if h else f"{m}:{s:02d}"
            views_s=f"{views:,}" if views else "—"
            thumb=info.get("thumbnail") or (info.get("thumbnails") or [{}])[-1].get("url")
            self.after(0,lambda: self._show_preview(title,chan,dur_s,views_s,date,thumb))
        except Exception as e:
            msg=str(e).split("\n")[0][:180]
            self.after(0,lambda: (self._set_status(msg,"#e74c3c"), self.fetch_btn.configure(state="normal",text="Fetch")))

    def _show_preview(self,title,chan,dur,views,date,thumb):
        self.title_l.configure(text=title)
        self.chan_l.configure(text=chan)
        self.pill_dur.configure(text=f"⏱  {dur}")
        self.pill_views.configure(text=f"👁  {views}")
        self.pill_date.configure(text=f"📅  {date or '—'}")
        self._set_status("✓ Ready","#2ecc71")
        self.fetch_btn.configure(state="normal",text="Fetch")
        self.dl_btn.configure(state="normal")
        self.bar.set(0); self.pct_l.configure(text="0%"); self.speed_l.configure(text=""); self.eta_l.configure(text="")
        self._refresh_dl_text()
        if thumb: threading.Thread(target=self._load_thumb,args=(thumb,dur),daemon=True).start()

    def _load_thumb(self,url,dur):
        try:
            r=requests.get(url,timeout=8); im=Image.open(BytesIO(r.content)).convert("RGB")
            im.thumbnail((520,292),Image.LANCZOS)
            cim=ctk.CTkImage(light_image=im,dark_image=im,size=im.size)
            self.thumb=cim
            self.after(0,lambda: (self.thumb_label.configure(image=cim,text=""), self.badge.configure(text=f" {dur} "), self.badge.place(relx=1.0,rely=1.0,anchor="se",x=-8,y=-8)))
        except: pass

    def _download(self):
        if not self.info: self._set_status("Fetch a video first","#e74c3c"); return
        url=self.url.get().strip()
        fmt=self.fmt_var.get(); qual=self.qual_var.get()
        self.dl_btn.configure(state="disabled",text="Downloading…")
        self.bar.set(0.03); self.pct_l.configure(text="1%")
        self._set_status("Starting…",MUTED)
        threading.Thread(target=self._dl_t,args=(url,fmt,qual),daemon=True).start()

    def _dl_t(self,url,fmt,qual):
        stats={"done":0,"skipped":0}
        err_msgs=[]

        class _BatchLogger:
            def debug(self,msg): pass
            def info(self,msg): pass
            def _count(self,msg):
                m=str(msg).split("\n")[0][:200]
                # yt-dlp routes per-video failures here (private/deleted/unavailable)
                # via report_error AND report_warning when ignoreerrors=True.
                # Dedupe by message (messages embed the video id) to avoid
                # double-counting the same video from both paths.
                if m not in err_msgs:
                    err_msgs.append(m)
                    stats["skipped"]=len(err_msgs)
            def warning(self,msg): self._count(msg)
            def error(self,msg): self._count(msg)

        def hook(d):
            if d["status"]=="downloading":
                tot=d.get("total_bytes") or d.get("total_bytes_estimate") or 0
                done=d.get("downloaded_bytes") or 0
                pct=done/tot if tot else 0
                sp=d.get("_speed_str","").strip(); eta=d.get("_eta_str","").strip()
                info=d.get("info_dict") or {}
                idx=info.get("playlist_index"); cnt=info.get("playlist_count")
                prefix=f"[{idx}/{cnt}] " if idx and cnt else ""
                title=(info.get("title") or "")[:40]
                self.after(0,lambda p=pct,sp=sp,eta=eta,prefix=prefix,title=title: (self.bar.set(max(0.03,p)), self.pct_l.configure(text=f"{int(p*100)}%"),
                                       self.speed_l.configure(text=f"{prefix}{title} {sp}".strip()), self.eta_l.configure(text=f"ETA {eta}" if eta else ""),
                                       self._set_status(f"{prefix}Downloading… {int(p*100)}%")))
            elif d["status"]=="finished":
                stats["done"]+=1
                info=d.get("info_dict") or {}
                idx=info.get("playlist_index"); cnt=info.get("playlist_count")
                prefix=f"[{idx}/{cnt}] " if idx and cnt else ""
                self.after(0,lambda prefix=prefix: (self._set_status(f"{prefix}Merging & converting…","#f1c40f"), self.bar.set(0.97)))

        out=str(Path(self.folder)/"%(title)s.%(ext)s")
        is_mp3=fmt=="MP3"
        qmap={"320 kbps":"320","256 kbps":"256","192 kbps":"192","128 kbps":"128"}
        # Robust formats with fallbacks — fixes "Requested format is not available"
        vmap={
            "Best":"bv*+ba/b",
            "1080p":"bv*[height<=1080]+ba/b[height<=1080] / bv*+ba/b",
            "720p":"bv*[height<=720]+ba/b[height<=720] / bv*+ba/b",
            "480p":"bv*[height<=480]+ba/b[height<=480] / bv*+ba/b",
            "360p":"bv*[height<=360]+ba/b[height<=360] / bv*+ba/b",
        }
        base_opts={"outtmpl":out,"progress_hooks":[hook],"logger":_BatchLogger(),"noplaylist":not self.playlist_var.get(),
                   "quiet":True,"no_warnings":True,"windowsfilenames":True,"concurrent_fragment_downloads":4,
                   "http_chunk_size":10485760,
                   # --- batch robustness: skip private/deleted instead of aborting/sticking ---
                   "ignoreerrors":True,"ignore_no_formats_error":True,"skip_unavailable_fragments":True,
                   "retries":10,"fragment_retries":10,"socket_timeout":30,"continuedl":True,"noprogress":True}

        def try_download(opts):
            with yt_dlp.YoutubeDL(opts) as ydl: ydl.download([url])
            # Single private video (not playlist): nothing downloaded, only errors
            if stats["done"]==0 and stats["skipped"]>0 and self.playlist_var.get() is False:
                raise Exception(err_msgs[-1] if err_msgs else "Video unavailable (private/deleted)")

        def ok_with_skips(msg=""):
            if stats["skipped"]>0 and stats["done"]>0:
                msg=(msg+" " if msg else "")+f"({stats['done']} saved, {stats['skipped']} skipped — private/unavailable)"
                return self._ok(msg)
            if stats["done"]==0 and stats["skipped"]>0:
                # playlist where everything was skipped
                return self._fail("All videos skipped — private/deleted/unavailable")
            return self._ok(msg)

        # --- MP3 ---
        if is_mp3:
            opts={**base_opts,"format":"bestaudio/best","postprocessors":[{"key":"FFmpegExtractAudio","preferredcodec":"mp3","preferredquality":qmap.get(qual,"320")}]}
            if self.split_var.get(): opts["postprocessors"].append({"key":"FFmpegSplitChapters","force":False})
            try:
                try_download(opts)
            except Exception as e:
                msg=str(e).lower()
                if "ffmpeg" in msg or "ffprobe" in msg:
                    opts.pop("postprocessors",None)
                    opts["format"]="bestaudio/best"
                    try:
                        try_download(opts)
                        return ok_with_skips("(install ffmpeg for true MP3)")
                    except Exception as e2: return self._fail(str(e2))
                if "requested format is not available" in msg or "video unavailable" in msg or "private" in msg or "deleted" in msg:
                    # private/deleted single video already reported via try_download;
                    # playlist partial failures don't raise, so only retry here for format issues
                    if "requested format is not available" in msg:
                        opts["format"]="bestaudio/best"; opts.pop("postprocessors",None)
                        try:
                            try_download(opts); return ok_with_skips()
                        except Exception as e2: return self._fail(str(e2))
                    return self._fail(str(e))
                else: return self._fail(str(e))
            return ok_with_skips()

        # --- MP4 ---
        opts={**base_opts,"format":vmap.get(qual,"bv*+ba/b"),"merge_output_format":"mp4"}
        try:
            try_download(opts)
            return ok_with_skips()
        except Exception as e:
            msg=str(e)
            low=msg.lower()
            if "requested format is not available" in low or "format is not available" in low:
                # fallback to best whatever
                opts["format"]="bv*+ba/b"
                try:
                    try_download(opts); return ok_with_skips()
                except Exception as e2: return self._fail(str(e2))
            if "ffmpeg" in low:
                opts.pop("merge_output_format",None)
                opts["format"]="best/bestvideo+bestaudio"
                try: try_download(opts); return ok_with_skips(msg="(no ffmpeg — saved as available container)")
                except Exception as e2: return self._fail(str(e2))
            return self._fail(msg)

    def _ok(self,msg=""):
        extra=f" {msg}" if msg else ""
        self.after(0,lambda:(self.bar.set(1),self.pct_l.configure(text="100%"),self._set_status(f"✓ Done — {self._short(self.folder)}{extra}","#2ecc71"),self.dl_btn.configure(state="normal"),self._refresh_dl_text(),self.speed_l.configure(text="Saved"),self.eta_l.configure(text="")))

    def _fail(self,msg):
        m=msg.split("\n")[0][:170]
        self.after(0,lambda:(self._set_status(f"✕ {m}","#e74c3c"),self.dl_btn.configure(state="normal"),self._refresh_dl_text(),self.bar.set(0),self.pct_l.configure(text="0%")))

if __name__=="__main__":
    App().mainloop()
