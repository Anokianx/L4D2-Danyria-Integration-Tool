# =============================================================================
# 模块说明：Danyria 主程序，负责主题界面、MOD 扫描、HUD 插件安装、外置 HUD 启动和设置保存。
# Module overview: Main Danyria application for themed UI, mod scanning, HUD plugin installation, external HUD launching, and settings persistence.
# =============================================================================

from __future__ import annotations

import io
import os
import re
import json
import time
import locale
import struct
import shutil
import subprocess
import runpy
import sys
import webbrowser
import zlib
import math
import queue
import threading
from dataclasses import dataclass, field, replace
from pathlib import Path
from typing import Optional

# ---------------------------------------------------------------------------
# HUD 运行时依赖预加载。HUD 作为数据文件通过 runpy 嵌入启动，打包器不会自动分析它的导入。
# HUD runtime dependency preload. The HUD is embedded as a data file via runpy, so packagers may not analyze its imports automatically.
# ---------------------------------------------------------------------------
_HUD_RUNTIME_IMPORTS = (math, queue, threading)

try:
    from PySide6.QtCore import (
        Qt, QSize, QPoint, QPointF, QRect, QTimer, QEvent,
        QPropertyAnimation, QEasingCurve
    )
    from PySide6.QtGui import QIcon, QPixmap, QColor, QPainter, QPen, QBrush, QPainterPath, QFont, QFontMetrics
    from PySide6.QtWidgets import (
        QApplication, QMainWindow, QWidget, QLabel, QPushButton, QLineEdit,
        QFileDialog, QMessageBox, QComboBox, QTableWidget, QTableWidgetItem,
        QAbstractItemView, QHeaderView, QVBoxLayout, QHBoxLayout, QGridLayout, QLayout, QFrame,
        QTextEdit, QSplitter, QSizeGrip, QSizePolicy, QGraphicsOpacityEffect,
        QDialog, QCheckBox, QStackedWidget, QScrollArea
    )
except Exception:
    from PyQt6.QtCore import (
        Qt, QSize, QPoint, QPointF, QRect, QTimer, QEvent,
        QPropertyAnimation, QEasingCurve
    )
    from PyQt6.QtGui import QIcon, QPixmap, QColor, QPainter, QPen, QBrush, QPainterPath, QFont, QFontMetrics
    from PyQt6.QtWidgets import (
        QApplication, QMainWindow, QWidget, QLabel, QPushButton, QLineEdit,
        QFileDialog, QMessageBox, QComboBox, QTableWidget, QTableWidgetItem,
        QAbstractItemView, QHeaderView, QVBoxLayout, QHBoxLayout, QGridLayout, QLayout, QFrame,
        QTextEdit, QSplitter, QSizeGrip, QSizePolicy, QGraphicsOpacityEffect,
        QDialog, QCheckBox, QStackedWidget, QScrollArea
    )

NativeQMessageBox = QMessageBox

# ---------------------------------------------------------------------------
# 应用常量和文件格式常量。
# Application constants and file-format constants.
# ---------------------------------------------------------------------------
APP_NAME = "Danyria"
APP_VERSION = "1.1.0 Experimental"
CONFIG_NAME = "danyria_config.json"
VPK_MAGIC = 0x55AA1234
DIR_INDEX = 0x7FFF
L4D2_APP_ID = "550"

# ---------------------------------------------------------------------------
# 主题调色板，分别描述布景之形和幻灭之形界面颜色。
# Theme palettes for Backdrop Form and Ruin Form.
# ---------------------------------------------------------------------------
THEMES = {
    "normal": {
        "label": "布景之形",
        "bg": "#FFF3FA",
        "bg2": "#F0FAFF",
        "panel": "#FFFDFF",
        "panel2": "#FFF1F8",
        "line": "#EFBED8",
        "text": "#2E2033",
        "muted": "#7C5C7D",
        "subtle": "#B4749C",
        "accent": "#8FD8F8",
        "accent2": "#F39AC7",
        "chip": "#FFF6FB",
        "chip_text": "#875C86",
        "button": "#FFF8FC",
        "button_text": "#302033",
        "button_hover_a": "#A7E2FF",
        "button_hover_b": "#FFA7D0",
        "accent_text": "#151019",
        "danger": "#D96F94",
        "good": "#54B8AA",
        "brand_title": "#E9A9C9",
        "brand_version": "#BD78A0",
        "brand_glow": "#FFE2F2",
        "title_file": "title_normal.png",
        "avatar_file": "avatar_normal.png",
        "target_avatar_file": "avatar_ruin.png",
    },
    "ruin": {
        "label": "幻灭之形",
        "bg": "#181025",
        "bg2": "#2B1738",
        "panel": "#231633",
        "panel2": "#301D45",
        "line": "#6D4B81",
        "text": "#F6EEFF",
        "muted": "#D0B6DE",
        "subtle": "#BF8FCE",
        "accent": "#B99DFF",
        "accent2": "#F095C8",
        "chip": "#38234F",
        "chip_text": "#EBD0F5",
        "button": "#2B1A3E",
        "button_text": "#F5ECFF",
        "button_hover_a": "#C3A5FF",
        "button_hover_b": "#FF9ACE",
        "accent_text": "#160F1F",
        "danger": "#E37AA4",
        "good": "#70C9CD",
        "brand_title": "#E8B0D2",
        "brand_version": "#D895BD",
        "brand_glow": "#432154",
        "title_file": "title_ruin.png",
        "avatar_file": "avatar_ruin.png",
        "target_avatar_file": "avatar_normal.png",
    },
}


I18N_BASE = "zh"

# ---------------------------------------------------------------------------
# 多语言文本表，界面文字统一从这里读取。
# Localization table used by all UI text.
# ---------------------------------------------------------------------------
I18N = {'zh': {'language_name': '中文',
        'settings': '设置',
        'settings_title': '设置',
        'theme': '主题',
        'theme_normal': '布景之形',
        'theme_ruin': '幻灭之形',
        'language': '语言',
        'lang_auto': '自动（按系统时区）',
        'startup': '开机自启动',
        'startup_unavailable': '开机自启动仅支持 Windows',
        'apply': '应用',
        'cancel': '取消',
        'path': 'L4D2 路径',
        'choose': '选择',
        'auto_detect': '自动识别',
        'scan': '扫描',
        'launch_l4d2': '启动 L4D2',
        'danyria_section': 'Danyria',
        'install_danyria': '安装 / 更新 Danyria',
        'launch_hud': '启动 Danyria HUD',
        'open_ems': '打开 ems 遥测目录',
        'mod_manage': 'MOD 管理',
        'drop_hint': '把 .vpk 拖进窗口即可安装到 addons',
        'open_selected': '打开选中项位置',
        'toggle_selected': '启用 / 禁用选中项',
        'open_addons': '打开 addons',
        'open_workshop': '打开 workshop',
        'details': '详细信息',
        'not_scanned': '未扫描',
        'scanned': '已扫描 {n} 项',
        'danyria_unknown': 'HUD 插件：未确认',
        'danyria_none': 'HUD 插件：未安装',
        'danyria_found': 'HUD 插件：{n} 项',
        'search_placeholder': '搜索真实标题、数字 ID、路径、作者、分类证据……',
        'filter_all_categories': '全部分类',
        'filter_all_sources': '全部来源',
        'filter_all_status': '全部状态',
        'col_name': '名称',
        'col_category': '分类',
        'col_status': '状态',
        'col_type': '类型',
        'col_source': '来源',
        'col_size': '大小',
        'col_id_evidence': 'ID / 证据',
        'detail_name': '名称',
        'detail_category': '分类',
        'detail_status': '状态',
        'detail_type': '类型',
        'detail_source': '来源',
        'detail_size': '大小',
        'detail_author': '作者',
        'detail_modified': '修改',
        'detail_tags': '标签',
        'detail_path': '路径',
        'detail_description': '描述',
        'detail_evidence': '分类证据',
        'none': '无',
        'select_first': '请先选择一个模组。',
        'not_exists': '文件或文件夹不存在。',
        'target_exists': '目标已存在：\n{path}\n\n请先改名或移走同名项目。',
        'open_failed': '打开失败',
        'missing_path': '请先选择正确的 left4dead2 文件夹。',
        'path_no_addons': '这个路径下面没有 addons。请选择 left4dead2 文件夹。',
        'auto_detect_ok': '已识别 L4D2 路径。',
        'auto_detect_fail': '没有自动识别到 L4D2，请手动选择 left4dead2 文件夹。',
        'operation_failed': '操作失败',
        'install_failed': '安装失败',
        'install_success': 'Danyria 已安装/更新。',
        'vpk_installed_title': 'VPK 已安装',
        'vpk_installed_body': '已安装到 addons：\n{items}',
        'nothing_installed_title': '没有安装',
        'nothing_installed_body': '拖入的文件里没有可安装的 .vpk。',
        'launch_failed': '启动失败',
        'launch_failed_body': '没有成功通过 Steam URL 或 left4dead2.exe 启动游戏。',
        'missing_file': '缺少文件',
        'missing_mod_payload': 'payload 中没有找到 danyria_mod。',
        'missing_hud': '缺少 HUD',
        'missing_hud_body': 'payload 中没有找到 DanyriaHUD.pyw。',
        'python_not_found': 'Python 未找到',
        'python_not_found_body': '没有找到 pythonw/pyw/python。',
        'choose_l4d2_folder': '选择 Left 4 Dead 2/left4dead2 文件夹',
        'category_Danyria': 'Danyria',
        'category_Campaign': '战役',
        'category_Map': '地图',
        'category_HUD / UI': 'HUD / UI',
        'category_Mutation / Script': '脚本 / 模式',
        'category_Character / Skin': '角色 / 皮肤',
        'category_Infected': '感染者',
        'category_Weapon': '武器',
        'category_Medical / Items': '医疗物品',
        'category_Throwables': '投掷物',
        'category_Carryables / Props': '可携带物 / 物件',
        'category_Sound / Music': '声音 / 音乐',
        'category_Effects / Particles': '特效 / 粒子',
        'category_Texture / Materials': '贴图 / 材质',
        'category_Props / World': '场景物件',
        'category_Unknown': '未知',
        'status_Enabled': '启用',
        'status_Disabled': '禁用',
        'status_Broken': '损坏',
        'kind_VPK': 'VPK',
        'kind_Folder': '文件夹',
        'detail_workshop_id': 'Workshop ID',
        'colon': '：',
        'source_Local': '本地',
        'source_Workshop': '创意工坊',
        'source_Unknown': '未知来源'},
 'en': {'language_name': 'English',
        'settings': 'Settings',
        'settings_title': 'Settings',
        'theme': 'Theme',
        'theme_normal': 'Backdrop Form',
        'theme_ruin': 'Ruin Form',
        'language': 'Language',
        'lang_auto': 'Auto by time zone',
        'startup': 'Launch at startup',
        'startup_unavailable': 'Windows only',
        'apply': 'Apply',
        'cancel': 'Cancel',
        'path': 'L4D2 Path',
        'choose': 'Choose',
        'auto_detect': 'Auto Detect',
        'scan': 'Scan',
        'launch_l4d2': 'Launch L4D2',
        'danyria_section': 'Danyria',
        'install_danyria': 'Install / Update Danyria',
        'launch_hud': 'Launch Danyria HUD',
        'open_ems': 'Open ems telemetry folder',
        'mod_manage': 'MOD Management',
        'drop_hint': 'Drag .vpk files here to install them to addons',
        'open_selected': 'Open selected item',
        'toggle_selected': 'Enable / Disable selected',
        'open_addons': 'Open addons',
        'open_workshop': 'Open workshop',
        'details': 'Details',
        'not_scanned': 'Not scanned',
        'scanned': 'Scanned {n}',
        'danyria_unknown': 'HUD plugin: unknown',
        'danyria_none': 'HUD plugin: not installed',
        'danyria_found': 'HUD plugin: {n}',
        'search_placeholder': 'Search title, numeric ID, path, author, category evidence…',
        'filter_all_categories': 'All categories',
        'filter_all_sources': 'All sources',
        'filter_all_status': 'All status',
        'col_name': 'Name',
        'col_category': 'Category',
        'col_status': 'Status',
        'col_type': 'Type',
        'col_source': 'Source',
        'col_size': 'Size',
        'col_id_evidence': 'ID / Evidence',
        'detail_name': 'Name',
        'detail_category': 'Category',
        'detail_status': 'Status',
        'detail_type': 'Type',
        'detail_source': 'Source',
        'detail_size': 'Size',
        'detail_author': 'Author',
        'detail_modified': 'Modified',
        'detail_tags': 'Tags',
        'detail_path': 'Path',
        'detail_description': 'Description',
        'detail_evidence': 'Classification evidence',
        'none': 'None',
        'select_first': 'Select a mod first.',
        'not_exists': 'The file or folder does not exist.',
        'target_exists': 'Target already exists:\n{path}\n\nRename or move the duplicate first.',
        'open_failed': 'Open failed',
        'missing_path': 'Select a valid left4dead2 folder first.',
        'path_no_addons': 'This folder has no addons directory. Select the left4dead2 folder.',
        'auto_detect_ok': 'L4D2 path detected.',
        'auto_detect_fail': 'L4D2 was not detected. Choose the left4dead2 folder manually.',
        'operation_failed': 'Operation failed',
        'install_failed': 'Install failed',
        'install_success': 'Danyria has been installed/updated.',
        'vpk_installed_title': 'VPK installed',
        'vpk_installed_body': 'Installed to addons:\n{items}',
        'nothing_installed_title': 'Nothing installed',
        'nothing_installed_body': 'The dropped files did not include an installable .vpk.',
        'launch_failed': 'Launch failed',
        'launch_failed_body': 'Could not launch through the Steam URL or left4dead2.exe.',
        'missing_file': 'Missing file',
        'missing_mod_payload': 'danyria_mod was not found in payload.',
        'missing_hud': 'Missing HUD',
        'missing_hud_body': 'DanyriaHUD.pyw was not found in payload.',
        'python_not_found': 'Python not found',
        'python_not_found_body': 'pythonw/pyw/python was not found.',
        'choose_l4d2_folder': 'Choose the Left 4 Dead 2/left4dead2 folder',
        'category_Danyria': 'Danyria',
        'category_Campaign': 'Campaign',
        'category_Map': 'Map',
        'category_HUD / UI': 'HUD / UI',
        'category_Mutation / Script': 'Mutation / Script',
        'category_Character / Skin': 'Character / Skin',
        'category_Infected': 'Infected',
        'category_Weapon': 'Weapon',
        'category_Medical / Items': 'Medical / Items',
        'category_Throwables': 'Throwables',
        'category_Carryables / Props': 'Carryables / Props',
        'category_Sound / Music': 'Sound / Music',
        'category_Effects / Particles': 'Effects / Particles',
        'category_Texture / Materials': 'Texture / Materials',
        'category_Props / World': 'Props / World',
        'category_Unknown': 'Unknown',
        'status_Enabled': 'Enabled',
        'status_Disabled': 'Disabled',
        'status_Broken': 'Broken',
        'kind_VPK': 'VPK',
        'kind_Folder': 'Folder',
        'detail_workshop_id': 'Workshop ID',
        'colon': ': ',
        'source_Local': 'Local',
        'source_Workshop': 'Workshop',
        'source_Unknown': 'Unknown source'},
 'ja': {'language_name': '日本語',
        'settings': '設定',
        'settings_title': '設定',
        'theme': 'テーマ',
        'theme_normal': '布景の形',
        'theme_ruin': '幻滅の形',
        'language': '言語',
        'lang_auto': '自動（システム時刻帯）',
        'startup': '起動時に自動起動',
        'startup_unavailable': '自動起動は Windows のみ対応',
        'apply': '適用',
        'cancel': 'キャンセル',
        'path': 'L4D2 パス',
        'choose': '選択',
        'auto_detect': '自動検出',
        'scan': 'スキャン',
        'launch_l4d2': 'L4D2 起動',
        'danyria_section': 'Danyria',
        'install_danyria': 'Danyria をインストール / 更新',
        'launch_hud': 'Danyria HUD 起動',
        'open_ems': 'ems テレメトリフォルダーを開く',
        'mod_manage': 'MOD管理',
        'drop_hint': '.vpk をここにドラッグして addons にインストール',
        'open_selected': '選択項目を開く',
        'toggle_selected': '選択項目を有効 / 無効',
        'open_addons': 'addons を開く',
        'open_workshop': 'workshop を開く',
        'details': '詳細',
        'not_scanned': '未スキャン',
        'scanned': 'スキャン済み {n}',
        'danyria_unknown': 'Danyria: 未確認',
        'danyria_none': 'Danyria: 未インストール',
        'danyria_found': 'HUD plugin: {n}',
        'search_placeholder': 'タイトル、数字 ID、パス、作者、分類根拠を検索…',
        'filter_all_categories': 'すべての分類',
        'filter_all_sources': 'すべてのソース',
        'filter_all_status': 'すべての状態',
        'col_name': '名前',
        'col_category': '分類',
        'col_status': '状態',
        'col_type': '種類',
        'col_source': 'ソース',
        'col_size': 'サイズ',
        'col_id_evidence': 'ID / 根拠',
        'detail_name': '名前',
        'detail_category': '分類',
        'detail_status': '状態',
        'detail_type': '種類',
        'detail_source': 'ソース',
        'detail_size': 'サイズ',
        'detail_author': '作者',
        'detail_modified': '更新日時',
        'detail_tags': 'タグ',
        'detail_path': 'パス',
        'detail_description': '説明',
        'detail_evidence': '分類根拠',
        'none': 'なし',
        'select_first': '先に MOD を選択してください。',
        'not_exists': 'ファイルまたはフォルダーが存在しません。',
        'target_exists': '対象がすでに存在します:\n{path}\n\n先に名前を変更するか移動してください。',
        'open_failed': '開くのに失敗しました',
        'missing_path': '正しい left4dead2 フォルダーを選択してください。',
        'path_no_addons': 'このフォルダーには addons がありません。left4dead2 フォルダーを選択してください。',
        'auto_detect_ok': 'L4D2 パスを検出しました。',
        'auto_detect_fail': 'L4D2 を検出できませんでした。手動で left4dead2 フォルダーを選択してください。',
        'operation_failed': '操作に失敗しました',
        'install_failed': 'インストール失敗',
        'install_success': 'Danyria をインストール / 更新しました。',
        'vpk_installed_title': 'VPK をインストールしました',
        'vpk_installed_body': 'addons にインストールしました:\n{items}',
        'nothing_installed_title': 'インストールなし',
        'nothing_installed_body': 'ドロップされたファイルにインストール可能な .vpk がありません。',
        'launch_failed': '起動失敗',
        'launch_failed_body': 'Steam URL または left4dead2.exe でゲームを起動できませんでした。',
        'missing_file': 'ファイル不足',
        'missing_mod_payload': 'payload に danyria_mod が見つかりません。',
        'missing_hud': 'HUD がありません',
        'missing_hud_body': 'payload に DanyriaHUD.pyw が見つかりません。',
        'python_not_found': 'Python が見つかりません',
        'python_not_found_body': 'pythonw / pyw / python が見つかりません。',
        'choose_l4d2_folder': 'left4dead2 フォルダーを選択',
        'category_Danyria': 'Danyria',
        'category_Campaign': 'キャンペーン',
        'category_Map': 'マップ',
        'category_HUD / UI': 'HUD / UI',
        'category_Mutation / Script': 'ミューテーション / スクリプト',
        'category_Character / Skin': 'キャラクター / スキン',
        'category_Infected': '感染者',
        'category_Weapon': '武器',
        'category_Medical / Items': '医療アイテム',
        'category_Throwables': '投擲アイテム',
        'category_Carryables / Props': '運搬物 / プロップ',
        'category_Sound / Music': 'サウンド / 音楽',
        'category_Effects / Particles': 'エフェクト / パーティクル',
        'category_Texture / Materials': 'テクスチャ / マテリアル',
        'category_Props / World': 'ワールドプロップ',
        'category_Unknown': '不明',
        'status_Enabled': '有効',
        'status_Disabled': '無効',
        'status_Broken': '破損',
        'kind_VPK': 'VPK',
        'kind_Folder': 'フォルダー',
        'detail_workshop_id': 'Workshop ID',
        'colon': '：',
        'source_Local': 'ローカル',
        'source_Workshop': 'ワークショップ',
        'source_Unknown': '不明なソース'},
 'ko': {'language_name': '한국어',
        'settings': '설정',
        'settings_title': '설정',
        'theme': '테마',
        'theme_normal': '배경 형태',
        'theme_ruin': '환멸 형태',
        'language': '언어',
        'lang_auto': '자동(시스템 시간대)',
        'startup': '시작 시 자동 실행',
        'startup_unavailable': '자동 실행은 Windows에서만 지원됩니다',
        'apply': '적용',
        'cancel': '취소',
        'path': 'L4D2 경로',
        'choose': '선택',
        'auto_detect': '자동 감지',
        'scan': '스캔',
        'launch_l4d2': 'L4D2 실행',
        'danyria_section': 'Danyria',
        'install_danyria': 'Danyria 설치 / 업데이트',
        'launch_hud': 'Danyria HUD 실행',
        'open_ems': 'ems 텔레메트리 폴더 열기',
        'mod_manage': 'MOD 관리',
        'drop_hint': '.vpk 파일을 여기로 끌어 addons에 설치',
        'open_selected': '선택한 항목 열기',
        'toggle_selected': '선택 항목 활성화 / 비활성화',
        'open_addons': 'addons 열기',
        'open_workshop': 'workshop 열기',
        'details': '상세 정보',
        'not_scanned': '스캔 안 됨',
        'scanned': '스캔됨 {n}',
        'danyria_unknown': 'Danyria: 확인 안 됨',
        'danyria_none': 'Danyria: 설치 안 됨',
        'danyria_found': 'HUD plugin: {n}',
        'search_placeholder': '제목, 숫자 ID, 경로, 작성자, 분류 근거 검색…',
        'filter_all_categories': '모든 분류',
        'filter_all_sources': '모든 소스',
        'filter_all_status': '모든 상태',
        'col_name': '이름',
        'col_category': '분류',
        'col_status': '상태',
        'col_type': '유형',
        'col_source': '소스',
        'col_size': '크기',
        'col_id_evidence': 'ID / 근거',
        'detail_name': '이름',
        'detail_category': '분류',
        'detail_status': '상태',
        'detail_type': '유형',
        'detail_source': '소스',
        'detail_size': '크기',
        'detail_author': '작성자',
        'detail_modified': '수정됨',
        'detail_tags': '태그',
        'detail_path': '경로',
        'detail_description': '설명',
        'detail_evidence': '분류 근거',
        'none': '없음',
        'select_first': '먼저 모드를 선택하세요.',
        'not_exists': '파일 또는 폴더가 없습니다.',
        'target_exists': '대상이 이미 존재합니다:\n{path}\n\n먼저 이름을 바꾸거나 이동하세요.',
        'open_failed': '열기 실패',
        'missing_path': '올바른 left4dead2 폴더를 먼저 선택하세요.',
        'path_no_addons': '이 폴더에는 addons 디렉터리가 없습니다. left4dead2 폴더를 선택하세요.',
        'auto_detect_ok': 'L4D2 경로를 감지했습니다.',
        'auto_detect_fail': 'L4D2를 감지하지 못했습니다. left4dead2 폴더를 수동으로 선택하세요.',
        'operation_failed': '작업 실패',
        'install_failed': '설치 실패',
        'install_success': 'Danyria가 설치/업데이트되었습니다.',
        'vpk_installed_title': 'VPK 설치됨',
        'vpk_installed_body': 'addons에 설치됨:\n{items}',
        'nothing_installed_title': '설치된 항목 없음',
        'nothing_installed_body': '끌어온 파일에 설치 가능한 .vpk가 없습니다.',
        'launch_failed': '실행 실패',
        'launch_failed_body': 'Steam URL 또는 left4dead2.exe로 게임을 실행하지 못했습니다.',
        'missing_file': '파일 누락',
        'missing_mod_payload': 'payload에서 danyria_mod를 찾을 수 없습니다.',
        'missing_hud': 'HUD 누락',
        'missing_hud_body': 'payload에서 DanyriaHUD.pyw를 찾을 수 없습니다.',
        'python_not_found': 'Python을 찾을 수 없음',
        'python_not_found_body': 'pythonw/pyw/python을 찾을 수 없습니다.',
        'choose_l4d2_folder': 'left4dead2 폴더 선택',
        'category_Danyria': 'Danyria',
        'category_Campaign': '캠페인',
        'category_Map': '맵',
        'category_HUD / UI': 'HUD / UI',
        'category_Mutation / Script': '뮤테이션 / 스크립트',
        'category_Character / Skin': '캐릭터 / 스킨',
        'category_Infected': '감염자',
        'category_Weapon': '무기',
        'category_Medical / Items': '의료 아이템',
        'category_Throwables': '투척물',
        'category_Carryables / Props': '운반물 / 소품',
        'category_Sound / Music': '사운드 / 음악',
        'category_Effects / Particles': '효과 / 파티클',
        'category_Texture / Materials': '텍스처 / 재질',
        'category_Props / World': '월드 소품',
        'category_Unknown': '알 수 없음',
        'status_Enabled': '활성화',
        'status_Disabled': '비활성화',
        'status_Broken': '손상됨',
        'kind_VPK': 'VPK',
        'kind_Folder': '폴더',
        'detail_workshop_id': 'Workshop ID',
        'colon': ': ',
        'source_Local': '로컬',
        'source_Workshop': '워크숍',
        'source_Unknown': '알 수 없는 소스'},
 'ru': {'language_name': 'Русский',
        'settings': 'Настройки',
        'settings_title': 'Настройки',
        'theme': 'Тема',
        'theme_normal': 'Форма сцены',
        'theme_ruin': 'Форма распада',
        'language': 'Язык',
        'lang_auto': 'Авто по часовому поясу',
        'startup': 'Запускать при входе',
        'startup_unavailable': 'Автозапуск доступен только в Windows',
        'apply': 'Применить',
        'cancel': 'Отмена',
        'path': 'Путь L4D2',
        'choose': 'Выбрать',
        'auto_detect': 'Автоопределение',
        'scan': 'Сканировать',
        'launch_l4d2': 'Запустить L4D2',
        'danyria_section': 'Danyria',
        'install_danyria': 'Установить / обновить Danyria',
        'launch_hud': 'Запустить Danyria HUD',
        'open_ems': 'Открыть папку телеметрии ems',
        'mod_manage': 'Управление MOD',
        'drop_hint': 'Перетащите .vpk сюда, чтобы установить в addons',
        'open_selected': 'Открыть выбранное',
        'toggle_selected': 'Включить / отключить выбранное',
        'open_addons': 'Открыть addons',
        'open_workshop': 'Открыть workshop',
        'details': 'Сведения',
        'not_scanned': 'Не сканировано',
        'scanned': 'Сканировано {n}',
        'danyria_unknown': 'Danyria: не подтверждено',
        'danyria_none': 'Danyria: не установлено',
        'danyria_found': 'HUD plugin: {n}',
        'search_placeholder': 'Поиск по названию, числовому ID, пути, автору или признакам классификации…',
        'filter_all_categories': 'Все категории',
        'filter_all_sources': 'Все источники',
        'filter_all_status': 'Все состояния',
        'col_name': 'Название',
        'col_category': 'Категория',
        'col_status': 'Состояние',
        'col_type': 'Тип',
        'col_source': 'Источник',
        'col_size': 'Размер',
        'col_id_evidence': 'ID / признаки',
        'detail_name': 'Название',
        'detail_category': 'Категория',
        'detail_status': 'Состояние',
        'detail_type': 'Тип',
        'detail_source': 'Источник',
        'detail_size': 'Размер',
        'detail_author': 'Автор',
        'detail_modified': 'Изменено',
        'detail_tags': 'Теги',
        'detail_path': 'Путь',
        'detail_description': 'Описание',
        'detail_evidence': 'Признаки классификации',
        'none': 'Нет',
        'select_first': 'Сначала выберите мод.',
        'not_exists': 'Файл или папка не существует.',
        'target_exists': 'Цель уже существует:\n{path}\n\nСначала переименуйте или переместите дубликат.',
        'open_failed': 'Не удалось открыть',
        'missing_path': 'Сначала выберите корректную папку left4dead2.',
        'path_no_addons': 'В этой папке нет каталога addons. Выберите папку left4dead2.',
        'auto_detect_ok': 'Путь L4D2 найден.',
        'auto_detect_fail': 'L4D2 не найден. Выберите папку left4dead2 вручную.',
        'operation_failed': 'Операция не выполнена',
        'install_failed': 'Установка не удалась',
        'install_success': 'Danyria установлена/обновлена.',
        'vpk_installed_title': 'VPK установлен',
        'vpk_installed_body': 'Установлено в addons:\n{items}',
        'nothing_installed_title': 'Ничего не установлено',
        'nothing_installed_body': 'В перетащенных файлах нет устанавливаемого .vpk.',
        'launch_failed': 'Запуск не удался',
        'launch_failed_body': 'Не удалось запустить игру через Steam URL или left4dead2.exe.',
        'missing_file': 'Файл отсутствует',
        'missing_mod_payload': 'Не найден danyria_mod в payload.',
        'missing_hud': 'HUD отсутствует',
        'missing_hud_body': 'Не найден DanyriaHUD.pyw в payload.',
        'python_not_found': 'Python не найден',
        'python_not_found_body': 'Не найден pythonw/pyw/python.',
        'choose_l4d2_folder': 'Выбрать папку left4dead2',
        'category_Danyria': 'Danyria',
        'category_Campaign': 'Кампания',
        'category_Map': 'Карта',
        'category_HUD / UI': 'HUD / UI',
        'category_Mutation / Script': 'Мутация / скрипт',
        'category_Character / Skin': 'Персонаж / скин',
        'category_Infected': 'Заражённые',
        'category_Weapon': 'Оружие',
        'category_Medical / Items': 'Медицинские предметы',
        'category_Throwables': 'Метательные предметы',
        'category_Carryables / Props': 'Переносимые / объекты',
        'category_Sound / Music': 'Звук / музыка',
        'category_Effects / Particles': 'Эффекты / частицы',
        'category_Texture / Materials': 'Текстуры / материалы',
        'category_Props / World': 'Объекты мира',
        'category_Unknown': 'Неизвестно',
        'status_Enabled': 'Включено',
        'status_Disabled': 'Отключено',
        'status_Broken': 'Повреждено',
        'kind_VPK': 'VPK',
        'kind_Folder': 'Папка',
        'detail_workshop_id': 'Workshop ID',
        'colon': ': ',
        'source_Local': 'Локально',
        'source_Workshop': 'Мастерская',
        'source_Unknown': 'Неизвестный источник'},
 'de': {'language_name': 'Deutsch',
        'settings': 'Einstellungen',
        'settings_title': 'Einstellungen',
        'theme': 'Design',
        'theme_normal': 'Kulissenform',
        'theme_ruin': 'Verfallsform',
        'language': 'Sprache',
        'lang_auto': 'Automatisch nach Zeitzone',
        'startup': 'Beim Systemstart ausführen',
        'startup_unavailable': 'Autostart ist nur unter Windows verfügbar',
        'apply': 'Anwenden',
        'cancel': 'Abbrechen',
        'path': 'L4D2-Pfad',
        'choose': 'Auswählen',
        'auto_detect': 'Automatisch erkennen',
        'scan': 'Scannen',
        'launch_l4d2': 'L4D2 starten',
        'danyria_section': 'Danyria',
        'install_danyria': 'Danyria installieren / aktualisieren',
        'launch_hud': 'Danyria HUD starten',
        'open_ems': 'ems-Telemetrieordner öffnen',
        'mod_manage': 'MOD-Verwaltung',
        'drop_hint': '.vpk-Dateien hierher ziehen, um sie in addons zu installieren',
        'open_selected': 'Ausgewähltes Element öffnen',
        'toggle_selected': 'Ausgewähltes aktivieren / deaktivieren',
        'open_addons': 'addons öffnen',
        'open_workshop': 'workshop öffnen',
        'details': 'Details',
        'not_scanned': 'Nicht gescannt',
        'scanned': '{n} gescannt',
        'danyria_unknown': 'Danyria: unbekannt',
        'danyria_none': 'Danyria: nicht installiert',
        'danyria_found': 'HUD plugin: {n}',
        'search_placeholder': 'Nach Titel, numerischer ID, Pfad, Autor oder Klassifizierungsnachweis suchen…',
        'filter_all_categories': 'Alle Kategorien',
        'filter_all_sources': 'Alle Quellen',
        'filter_all_status': 'Alle Status',
        'col_name': 'Name',
        'col_category': 'Kategorie',
        'col_status': 'Status',
        'col_type': 'Typ',
        'col_source': 'Quelle',
        'col_size': 'Größe',
        'col_id_evidence': 'ID / Nachweis',
        'detail_name': 'Name',
        'detail_category': 'Kategorie',
        'detail_status': 'Status',
        'detail_type': 'Typ',
        'detail_source': 'Quelle',
        'detail_size': 'Größe',
        'detail_author': 'Autor',
        'detail_modified': 'Geändert',
        'detail_tags': 'Tags',
        'detail_path': 'Pfad',
        'detail_description': 'Beschreibung',
        'detail_evidence': 'Klassifizierungsnachweis',
        'none': 'Keine',
        'select_first': 'Bitte zuerst einen Mod auswählen.',
        'not_exists': 'Datei oder Ordner existiert nicht.',
        'target_exists': 'Ziel existiert bereits:\n{path}\n\nBitte zuerst umbenennen oder verschieben.',
        'open_failed': 'Öffnen fehlgeschlagen',
        'missing_path': 'Bitte zuerst einen gültigen left4dead2-Ordner auswählen.',
        'path_no_addons': 'Dieser Ordner enthält kein addons-Verzeichnis. Wähle den left4dead2-Ordner.',
        'auto_detect_ok': 'L4D2-Pfad erkannt.',
        'auto_detect_fail': 'L4D2 wurde nicht erkannt. Wähle den left4dead2-Ordner manuell.',
        'operation_failed': 'Vorgang fehlgeschlagen',
        'install_failed': 'Installation fehlgeschlagen',
        'install_success': 'Danyria wurde installiert/aktualisiert.',
        'vpk_installed_title': 'VPK installiert',
        'vpk_installed_body': 'In addons installiert:\n{items}',
        'nothing_installed_title': 'Nichts installiert',
        'nothing_installed_body': 'Die abgelegten Dateien enthielten keine installierbare .vpk.',
        'launch_failed': 'Start fehlgeschlagen',
        'launch_failed_body': 'Das Spiel konnte weder über Steam-URL noch über left4dead2.exe gestartet werden.',
        'missing_file': 'Datei fehlt',
        'missing_mod_payload': 'danyria_mod wurde in payload nicht gefunden.',
        'missing_hud': 'HUD fehlt',
        'missing_hud_body': 'DanyriaHUD.pyw wurde in payload nicht gefunden.',
        'python_not_found': 'Python nicht gefunden',
        'python_not_found_body': 'pythonw/pyw/python wurde nicht gefunden.',
        'choose_l4d2_folder': 'left4dead2-Ordner auswählen',
        'category_Danyria': 'Danyria',
        'category_Campaign': 'Kampagne',
        'category_Map': 'Karte',
        'category_HUD / UI': 'HUD / UI',
        'category_Mutation / Script': 'Mutation / Skript',
        'category_Character / Skin': 'Charakter / Skin',
        'category_Infected': 'Infizierte',
        'category_Weapon': 'Waffe',
        'category_Medical / Items': 'Medizinische Gegenstände',
        'category_Throwables': 'Wurfgegenstände',
        'category_Carryables / Props': 'Tragbare Objekte / Props',
        'category_Sound / Music': 'Sound / Musik',
        'category_Effects / Particles': 'Effekte / Partikel',
        'category_Texture / Materials': 'Texturen / Materialien',
        'category_Props / World': 'Weltobjekte',
        'category_Unknown': 'Unbekannt',
        'status_Enabled': 'Aktiviert',
        'status_Disabled': 'Deaktiviert',
        'status_Broken': 'Defekt',
        'kind_VPK': 'VPK',
        'kind_Folder': 'Ordner',
        'detail_workshop_id': 'Workshop ID',
        'colon': ': ',
        'source_Local': 'Lokal',
        'source_Workshop': 'Workshop',
        'source_Unknown': 'Unbekannte Quelle'},
 'fr': {'language_name': 'Français',
        'settings': 'Paramètres',
        'settings_title': 'Paramètres',
        'theme': 'Thème',
        'theme_normal': 'Forme de décor',
        'theme_ruin': 'Forme de ruine',
        'language': 'Langue',
        'lang_auto': 'Auto selon le fuseau horaire',
        'startup': 'Lancer au démarrage',
        'startup_unavailable': 'Le lancement au démarrage est réservé à Windows',
        'apply': 'Appliquer',
        'cancel': 'Annuler',
        'path': 'Chemin L4D2',
        'choose': 'Choisir',
        'auto_detect': 'Détection auto',
        'scan': 'Analyser',
        'launch_l4d2': 'Lancer L4D2',
        'danyria_section': 'Danyria',
        'install_danyria': 'Installer / mettre à jour Danyria',
        'launch_hud': 'Lancer le HUD Danyria',
        'open_ems': 'Ouvrir le dossier de télémétrie ems',
        'mod_manage': 'Gestion des MOD',
        'drop_hint': 'Glissez des fichiers .vpk ici pour les installer dans addons',
        'open_selected': 'Ouvrir l’élément sélectionné',
        'toggle_selected': 'Activer / désactiver la sélection',
        'open_addons': 'Ouvrir addons',
        'open_workshop': 'Ouvrir workshop',
        'details': 'Détails',
        'not_scanned': 'Non analysé',
        'scanned': '{n} analysés',
        'danyria_unknown': 'Danyria : inconnu',
        'danyria_none': 'Danyria : non installé',
        'danyria_found': 'Danyria : {n}',
        'search_placeholder': 'Rechercher titre, ID numérique, chemin, auteur ou preuve de classification…',
        'filter_all_categories': 'Toutes les catégories',
        'filter_all_sources': 'Toutes les sources',
        'filter_all_status': 'Tous les états',
        'col_name': 'Nom',
        'col_category': 'Catégorie',
        'col_status': 'État',
        'col_type': 'Type',
        'col_source': 'Source',
        'col_size': 'Taille',
        'col_id_evidence': 'ID / preuve',
        'detail_name': 'Nom',
        'detail_category': 'Catégorie',
        'detail_status': 'État',
        'detail_type': 'Type',
        'detail_source': 'Source',
        'detail_size': 'Taille',
        'detail_author': 'Auteur',
        'detail_modified': 'Modifié',
        'detail_tags': 'Tags',
        'detail_path': 'Chemin',
        'detail_description': 'Description',
        'detail_evidence': 'Preuve de classification',
        'none': 'Aucun',
        'select_first': 'Sélectionnez d’abord un mod.',
        'not_exists': 'Le fichier ou dossier n’existe pas.',
        'target_exists': 'La cible existe déjà :\n{path}\n\nRenommez ou déplacez d’abord le doublon.',
        'open_failed': 'Échec de l’ouverture',
        'missing_path': 'Sélectionnez d’abord un dossier left4dead2 valide.',
        'path_no_addons': 'Ce dossier ne contient pas de répertoire addons. Sélectionnez le dossier left4dead2.',
        'auto_detect_ok': 'Chemin L4D2 détecté.',
        'auto_detect_fail': 'L4D2 n’a pas été détecté. Choisissez manuellement le dossier left4dead2.',
        'operation_failed': 'Opération échouée',
        'install_failed': 'Installation échouée',
        'install_success': 'Danyria a été installé/mis à jour.',
        'vpk_installed_title': 'VPK installé',
        'vpk_installed_body': 'Installé dans addons :\n{items}',
        'nothing_installed_title': 'Rien installé',
        'nothing_installed_body': 'Les fichiers déposés ne contiennent aucun .vpk installable.',
        'launch_failed': 'Lancement échoué',
        'launch_failed_body': 'Impossible de lancer le jeu via l’URL Steam ou left4dead2.exe.',
        'missing_file': 'Fichier manquant',
        'missing_mod_payload': 'danyria_mod introuvable dans payload.',
        'missing_hud': 'HUD manquant',
        'missing_hud_body': 'DanyriaHUD.pyw introuvable dans payload.',
        'python_not_found': 'Python introuvable',
        'python_not_found_body': 'pythonw/pyw/python introuvable.',
        'choose_l4d2_folder': 'Choisir le dossier left4dead2',
        'category_Danyria': 'Danyria',
        'category_Campaign': 'Campagne',
        'category_Map': 'Carte',
        'category_HUD / UI': 'HUD / UI',
        'category_Mutation / Script': 'Mutation / script',
        'category_Character / Skin': 'Personnage / skin',
        'category_Infected': 'Infectés',
        'category_Weapon': 'Arme',
        'category_Medical / Items': 'Objets médicaux',
        'category_Throwables': 'Objets à lancer',
        'category_Carryables / Props': 'Objets transportables / props',
        'category_Sound / Music': 'Son / musique',
        'category_Effects / Particles': 'Effets / particules',
        'category_Texture / Materials': 'Textures / matériaux',
        'category_Props / World': 'Objets du monde',
        'category_Unknown': 'Inconnu',
        'status_Enabled': 'Activé',
        'status_Disabled': 'Désactivé',
        'status_Broken': 'Cassé',
        'kind_VPK': 'VPK',
        'kind_Folder': 'Dossier',
        'detail_workshop_id': 'Workshop ID',
        'colon': ' : ',
        'source_Local': 'Local',
        'source_Workshop': 'Workshop',
        'source_Unknown': 'Source inconnue'},
 'es': {'language_name': 'Español',
        'settings': 'Ajustes',
        'settings_title': 'Ajustes',
        'theme': 'Tema',
        'theme_normal': 'Forma de escenario',
        'theme_ruin': 'Forma de ruina',
        'language': 'Idioma',
        'lang_auto': 'Auto por zona horaria',
        'startup': 'Iniciar con Windows',
        'startup_unavailable': 'El inicio automático solo está disponible en Windows',
        'apply': 'Aplicar',
        'cancel': 'Cancelar',
        'path': 'Ruta de L4D2',
        'choose': 'Elegir',
        'auto_detect': 'Detectar automáticamente',
        'scan': 'Escanear',
        'launch_l4d2': 'Iniciar L4D2',
        'danyria_section': 'Danyria',
        'install_danyria': 'Instalar / actualizar Danyria',
        'launch_hud': 'Iniciar HUD de Danyria',
        'open_ems': 'Abrir carpeta de telemetría ems',
        'mod_manage': 'Gestión de MOD',
        'drop_hint': 'Arrastra archivos .vpk aquí para instalarlos en addons',
        'open_selected': 'Abrir elemento seleccionado',
        'toggle_selected': 'Activar / desactivar seleccionado',
        'open_addons': 'Abrir addons',
        'open_workshop': 'Abrir workshop',
        'details': 'Detalles',
        'not_scanned': 'Sin escanear',
        'scanned': 'Escaneados {n}',
        'danyria_unknown': 'Danyria: desconocido',
        'danyria_none': 'Danyria: no instalado',
        'danyria_found': 'HUD plugin: {n}',
        'search_placeholder': 'Buscar título, ID numérico, ruta, autor o evidencia de clasificación…',
        'filter_all_categories': 'Todas las categorías',
        'filter_all_sources': 'Todas las fuentes',
        'filter_all_status': 'Todos los estados',
        'col_name': 'Nombre',
        'col_category': 'Categoría',
        'col_status': 'Estado',
        'col_type': 'Tipo',
        'col_source': 'Fuente',
        'col_size': 'Tamaño',
        'col_id_evidence': 'ID / evidencia',
        'detail_name': 'Nombre',
        'detail_category': 'Categoría',
        'detail_status': 'Estado',
        'detail_type': 'Tipo',
        'detail_source': 'Fuente',
        'detail_size': 'Tamaño',
        'detail_author': 'Autor',
        'detail_modified': 'Modificado',
        'detail_tags': 'Etiquetas',
        'detail_path': 'Ruta',
        'detail_description': 'Descripción',
        'detail_evidence': 'Evidencia de clasificación',
        'none': 'Ninguno',
        'select_first': 'Selecciona primero un mod.',
        'not_exists': 'El archivo o la carpeta no existe.',
        'target_exists': 'El destino ya existe:\n{path}\n\nRenombra o mueve primero el duplicado.',
        'open_failed': 'Error al abrir',
        'missing_path': 'Selecciona primero una carpeta left4dead2 válida.',
        'path_no_addons': 'Esta carpeta no tiene directorio addons. Selecciona la carpeta left4dead2.',
        'auto_detect_ok': 'Ruta de L4D2 detectada.',
        'auto_detect_fail': 'No se detectó L4D2. Elige manualmente la carpeta left4dead2.',
        'operation_failed': 'Operación fallida',
        'install_failed': 'Instalación fallida',
        'install_success': 'Danyria se instaló/actualizó.',
        'vpk_installed_title': 'VPK instalado',
        'vpk_installed_body': 'Instalado en addons:\n{items}',
        'nothing_installed_title': 'Nada instalado',
        'nothing_installed_body': 'Los archivos arrastrados no contienen ningún .vpk instalable.',
        'launch_failed': 'Error al iniciar',
        'launch_failed_body': 'No se pudo iniciar el juego mediante la URL de Steam ni left4dead2.exe.',
        'missing_file': 'Falta un archivo',
        'missing_mod_payload': 'No se encontró danyria_mod en payload.',
        'missing_hud': 'Falta el HUD',
        'missing_hud_body': 'No se encontró DanyriaHUD.pyw en payload.',
        'python_not_found': 'Python no encontrado',
        'python_not_found_body': 'No se encontró pythonw/pyw/python.',
        'choose_l4d2_folder': 'Elegir carpeta left4dead2',
        'category_Danyria': 'Danyria',
        'category_Campaign': 'Campaña',
        'category_Map': 'Mapa',
        'category_HUD / UI': 'HUD / UI',
        'category_Mutation / Script': 'Mutación / script',
        'category_Character / Skin': 'Personaje / skin',
        'category_Infected': 'Infectados',
        'category_Weapon': 'Arma',
        'category_Medical / Items': 'Objetos médicos',
        'category_Throwables': 'Arrojadizos',
        'category_Carryables / Props': 'Transportables / props',
        'category_Sound / Music': 'Sonido / música',
        'category_Effects / Particles': 'Efectos / partículas',
        'category_Texture / Materials': 'Texturas / materiales',
        'category_Props / World': 'Objetos del mundo',
        'category_Unknown': 'Desconocido',
        'status_Enabled': 'Activado',
        'status_Disabled': 'Desactivado',
        'status_Broken': 'Dañado',
        'kind_VPK': 'VPK',
        'kind_Folder': 'Carpeta',
        'detail_workshop_id': 'Workshop ID',
        'colon': ': ',
        'source_Local': 'Local',
        'source_Workshop': 'Workshop',
        'source_Unknown': 'Fuente desconocida'}}

LANG_ORDER = ["auto", "zh", "en", "ja", "ko", "ru", "de", "fr", "es"]

I18N_HUD_REWORK = {
    "zh": {
        "page_plugins": "插件",
        "page_mods": "MOD 管理",
        "plugin_hud_title": "HUD 功能插件",
        "plugin_hud_subtitle": "外置 HUD：速度表 + 敌人血量显示。",
        "install_hud_plugin": "安装 / 更新 HUD 遥测插件",
        "launch_hud_overlay": "启动外置 HUD",
        "open_telemetry_folder": "打开 ems 遥测目录",
        "hud_plugin_status": "HUD 插件状态",
        "hud_plugin_desc": "Danyria 插件：写出速度、血量和敌人数据。",
        "hud_launch_hint": "",
        "speedometer": "速度表",
        "speedometer_desc": "显示当前幸存者移动速度、速度峰值和动态仪表盘。",
        "enemy_health": "敌人血量显示",
        "enemy_health_desc": "显示附近特感、Tank、Witch 的血量条和距离。",
        "hud_plugin_installed": "HUD 插件：已发现 {n} 项",
        "hud_plugin_missing": "HUD 插件：未安装",
        "hud_plugin_unknown": "HUD 插件：未确认",
        "missing_hud_plugin_payload": "payload 中没有找到 danyria_hud_plugin。",
        "hud_plugin_install_success": "HUD telemetry plugin installed.",
        "hud_plugin_install_failed": "HUD 插件安装失败",
    },
    "en": {
        "page_plugins": "Plugins",
        "page_mods": "MOD Management",
        "plugin_hud_title": "HUD Plugin",
        "plugin_hud_subtitle": "External HUD: speedometer + enemy health display.",
        "install_hud_plugin": "Install / Update HUD Telemetry Plugin",
        "launch_hud_overlay": "Launch External HUD",
        "open_telemetry_folder": "Open ems telemetry folder",
        "hud_plugin_status": "HUD Plugin Status",
        "hud_plugin_desc": "Danyria plugin: writes speed, health, and enemy data.",
        "hud_launch_hint": "",
        "speedometer": "Speedometer",
        "speedometer_desc": "Shows current survivor speed, peak speed, and a dynamic gauge.",
        "enemy_health": "Enemy health",
        "enemy_health_desc": "Shows health bars and distance for nearby special infected, Tanks, and Witches.",
        "hud_plugin_installed": "HUD plugin: found {n}",
        "hud_plugin_missing": "HUD plugin: not installed",
        "hud_plugin_unknown": "HUD plugin: unknown",
        "missing_hud_plugin_payload": "danyria_hud_plugin was not found in payload.",
        "hud_plugin_install_success": "HUD telemetry plugin installed.",
        "hud_plugin_install_failed": "HUD plugin install failed",
    },
    "ja": {
        "page_plugins": "プラグイン",
        "page_mods": "MOD管理",
        "plugin_hud_title": "HUD プラグイン",
        "plugin_hud_subtitle": "外部 HUD：速度計 + 敵の体力表示。テレメトリには addon で起動してください。",
        "install_hud_plugin": "HUD テレメトリをインストール / 更新",
        "launch_hud_overlay": "外部 HUD を起動",
        "open_telemetry_folder": "ems テレメトリを開く",
        "hud_plugin_status": "HUD プラグイン状態",
        "hud_plugin_desc": "ゲーム内プラグインはテレメトリを書き出すだけで、表示は外部 HUD が行います。",
        "hud_launch_hint": "",
        "speedometer": "速度計",
        "speedometer_desc": "現在速度、最高速度、動的ゲージを表示します。",
        "enemy_health": "敵の体力",
        "enemy_health_desc": "周囲の特殊感染者、Tank、Witch の体力バーと距離を表示します。",
        "hud_plugin_installed": "HUD プラグイン：{n} 件",
        "hud_plugin_missing": "HUD プラグイン：未インストール",
        "hud_plugin_unknown": "HUD プラグイン：未確認",
        "missing_hud_plugin_payload": "payload に danyria_hud_plugin がありません。",
        "hud_plugin_install_success": "HUD telemetry plugin installed.",
        "hud_plugin_install_failed": "HUD プラグインのインストールに失敗",
    },
    "ko": {
        "page_plugins": "플러그인",
        "page_mods": "MOD 관리",
        "plugin_hud_title": "HUD 플러그인",
        "plugin_hud_subtitle": "외부 HUD: 속도계 + 적 체력 표시. 설치 후 일반 로컬/호스트 캠페인에서 텔레메트리를 자동 로드합니다.",
        "install_hud_plugin": "HUD 텔레메트리 설치 / 업데이트",
        "launch_hud_overlay": "외부 HUD 실행",
        "open_telemetry_folder": "ems 텔레메트리 열기",
        "hud_plugin_status": "HUD 플러그인 상태",
        "hud_plugin_desc": "게임 내 플러그인은 텔레메트리 파일만 쓰고, 표시는 외부 HUD가 처리합니다.",
        "hud_launch_hint": "",
        "speedometer": "속도계",
        "speedometer_desc": "현재 속도, 최고 속도, 동적 게이지를 표시합니다.",
        "enemy_health": "적 체력",
        "enemy_health_desc": "주변 특수 감염자, Tank, Witch의 체력과 거리를 표시합니다.",
        "hud_plugin_installed": "HUD 플러그인: {n}개 발견",
        "hud_plugin_missing": "HUD 플러그인: 미설치",
        "hud_plugin_unknown": "HUD 플러그인: 미확인",
        "missing_hud_plugin_payload": "payload에서 danyria_hud_plugin을 찾을 수 없습니다.",
        "hud_plugin_install_success": "HUD telemetry plugin installed.",
        "hud_plugin_install_failed": "HUD 플러그인 설치 실패",
    },
    "ru": {
        "page_plugins": "Плагины",
        "page_mods": "Управление MOD",
        "plugin_hud_title": "HUD-плагин",
        "plugin_hud_subtitle": "Внешний HUD: спидометр + здоровье врагов. Запускайте кампанию через addon для телеметрии.",
        "install_hud_plugin": "Установить / обновить HUD-телеметрию",
        "launch_hud_overlay": "Запустить внешний HUD",
        "open_telemetry_folder": "Открыть папку ems",
        "hud_plugin_status": "Состояние HUD-плагина",
        "hud_plugin_desc": "Игровой плагин только пишет телеметрию; интерфейс рисует внешняя программа.",
        "hud_launch_hint": "",
        "speedometer": "Спидометр",
        "speedometer_desc": "Показывает текущую скорость, пик и динамический индикатор.",
        "enemy_health": "Здоровье врагов",
        "enemy_health_desc": "Показывает здоровье и дистанцию особых заражённых, Tank и Witch.",
        "hud_plugin_installed": "HUD-плагин: найдено {n}",
        "hud_plugin_missing": "HUD-плагин: не установлен",
        "hud_plugin_unknown": "HUD-плагин: неизвестно",
        "missing_hud_plugin_payload": "В payload нет danyria_hud_plugin.",
        "hud_plugin_install_success": "HUD telemetry plugin installed.",
        "hud_plugin_install_failed": "Ошибка установки HUD-плагина",
    },
    "de": {
        "page_plugins": "Plugins",
        "page_mods": "MOD-Verwaltung",
        "plugin_hud_title": "HUD-Plugin",
        "plugin_hud_subtitle": "Externes HUD: Tacho + Gegnergesundheit. Kampagne per addon starten, damit Telemetrie verfügbar ist.",
        "install_hud_plugin": "HUD-Telemetrie installieren / aktualisieren",
        "launch_hud_overlay": "Externes HUD starten",
        "open_telemetry_folder": "ems-Telemetrie öffnen",
        "hud_plugin_status": "HUD-Plugin-Status",
        "hud_plugin_desc": "Das Ingame-Plugin schreibt nur Telemetrie; die Anzeige übernimmt das externe HUD.",
        "hud_launch_hint": "",
        "speedometer": "Tacho",
        "speedometer_desc": "Zeigt aktuelle Geschwindigkeit, Spitzenwert und dynamische Anzeige.",
        "enemy_health": "Gegnergesundheit",
        "enemy_health_desc": "Zeigt Lebensbalken und Entfernung für Spezialinfizierte, Tanks und Witches.",
        "hud_plugin_installed": "HUD-Plugin: {n} gefunden",
        "hud_plugin_missing": "HUD-Plugin: nicht installiert",
        "hud_plugin_unknown": "HUD-Plugin: unbekannt",
        "missing_hud_plugin_payload": "danyria_hud_plugin fehlt im payload.",
        "hud_plugin_install_success": "HUD telemetry plugin installed.",
        "hud_plugin_install_failed": "HUD-Plugin-Installation fehlgeschlagen",
    },
    "fr": {
        "page_plugins": "Plugins",
        "page_mods": "Gestion des MOD",
        "plugin_hud_title": "Plugin HUD",
        "plugin_hud_subtitle": "HUD externe : compteur de vitesse + santé des ennemis. Lancez la campagne avec la addon pour la télémétrie.",
        "install_hud_plugin": "Installer / mettre à jour la télémétrie HUD",
        "launch_hud_overlay": "Lancer le HUD externe",
        "open_telemetry_folder": "Ouvrir le dossier ems",
        "hud_plugin_status": "État du plugin HUD",
        "hud_plugin_desc": "Le plugin en jeu écrit seulement la télémétrie ; l’interface est rendue par le HUD externe.",
        "hud_launch_hint": "",
        "speedometer": "Compteur de vitesse",
        "speedometer_desc": "Affiche la vitesse actuelle, le pic et une jauge dynamique.",
        "enemy_health": "Santé des ennemis",
        "enemy_health_desc": "Affiche la santé et la distance des infectés spéciaux, Tanks et Witches.",
        "hud_plugin_installed": "Plugin HUD : {n} trouvé(s)",
        "hud_plugin_missing": "Plugin HUD : non installé",
        "hud_plugin_unknown": "Plugin HUD : inconnu",
        "missing_hud_plugin_payload": "danyria_hud_plugin est absent du payload.",
        "hud_plugin_install_success": "HUD telemetry plugin installed.",
        "hud_plugin_install_failed": "Échec de l’installation du plugin HUD",
    },
    "es": {
        "page_plugins": "Plugins",
        "page_mods": "Gestión de MOD",
        "plugin_hud_title": "Plugin HUD",
        "plugin_hud_subtitle": "HUD externo: velocímetro + salud de enemigos. Inicia la campaña con la mutación para obtener telemetría.",
        "install_hud_plugin": "Instalar / actualizar telemetría HUD",
        "launch_hud_overlay": "Iniciar HUD externo",
        "open_telemetry_folder": "Abrir carpeta ems",
        "hud_plugin_status": "Estado del plugin HUD",
        "hud_plugin_desc": "El plugin del juego solo escribe telemetría; la interfaz la muestra el HUD externo.",
        "hud_launch_hint": "",
        "speedometer": "Velocímetro",
        "speedometer_desc": "Muestra velocidad actual, máxima y un indicador dinámico.",
        "enemy_health": "Salud de enemigos",
        "enemy_health_desc": "Muestra barras de salud y distancia de infectados especiales, Tanks y Witches.",
        "hud_plugin_installed": "Plugin HUD: {n} encontrado(s)",
        "hud_plugin_missing": "Plugin HUD: no instalado",
        "hud_plugin_unknown": "Plugin HUD: desconocido",
        "missing_hud_plugin_payload": "No se encontró danyria_hud_plugin en payload.",
        "hud_plugin_install_success": "HUD telemetry plugin installed.",
        "hud_plugin_install_failed": "Error al instalar el plugin HUD",
    },
}

for _lang, _extra in I18N_HUD_REWORK.items():
    if _lang in I18N:
        I18N[_lang].update(_extra)

I18N_HUD_SPLIT = {
    "zh": {
        "hud_windows_title": "HUD 窗口设置",
        "hud_settings_hint": "速度表和血量显示已分成两个透明窗口。拖动 HUD 窗口调整位置；这里仅调样式参数，保存后重启外置 HUD 生效。",
        "speed_window": "速度表窗口",
        "enemy_window": "血量窗口",
        "hud_x": "X",
        "hud_y": "Y",
        "hud_scale": "缩放",
        "hud_opacity": "不透明度",
        "hud_max_speed": "速度表最大值",
        "hud_max_enemies": "最大敌人条数",
        "hud_save_settings": "保存 HUD 参数",
        "hud_reset_settings": "恢复默认 HUD 参数",
        "hud_settings_saved": "HUD 参数已保存。重启外置 HUD 后生效。",
        "hud_settings_reset": "HUD 参数已恢复默认。重启外置 HUD 后生效。",
        "hud_transparent_note": "窗口背景完全透明，只显示速度表线条和血量条。窗口可拖动。",
        "telemetry_not_generated_title": "HUD 数据提示",
        "telemetry_not_generated_body": "未检测到 HUD 数据。请确认 Danyria 插件已启用，并且游戏正在运行。",
    },
    "en": {
        "hud_windows_title": "HUD Window Settings",
        "hud_settings_hint": "The speedometer and health display are separate transparent windows. Drag HUD windows to position them; only style parameters are configured here.",
        "speed_window": "Speedometer window",
        "enemy_window": "Health window",
        "hud_x": "X",
        "hud_y": "Y",
        "hud_scale": "Scale",
        "hud_opacity": "Opacity",
        "hud_max_speed": "Speedometer max",
        "hud_max_enemies": "Max enemy bars",
        "hud_save_settings": "Save HUD Settings",
        "hud_reset_settings": "Reset HUD Settings",
        "hud_settings_saved": "HUD settings saved. Restart the external HUD to apply them.",
        "hud_settings_reset": "HUD settings reset. Restart the external HUD to apply them.",
        "hud_transparent_note": "The background is fully transparent. Only speedometer lines and health bars are drawn. Windows are draggable.",
        "telemetry_not_generated_title": "HUD data note",
        "telemetry_not_generated_body": "No HUD data was detected. Make sure the Danyria plugin is enabled and the game is running.",
    },
    "ja": {
        "hud_windows_title": "HUD ウィンドウ設定",
        "hud_settings_hint": "速度計と体力表示を別々の透明ウィンドウにしました。保存後、外部 HUD を再起動してください。",
        "speed_window": "速度計ウィンドウ",
        "enemy_window": "体力ウィンドウ",
        "hud_x": "X",
        "hud_y": "Y",
        "hud_scale": "拡大率",
        "hud_opacity": "不透明度",
        "hud_max_speed": "速度計の最大値",
        "hud_max_enemies": "敵バー最大数",
        "hud_save_settings": "HUD 設定を保存",
        "hud_reset_settings": "HUD 設定を初期化",
        "hud_settings_saved": "HUD 設定を保存しました。外部 HUD を再起動すると反映されます。",
        "hud_settings_reset": "HUD 設定を初期化しました。外部 HUD を再起動すると反映されます。",
        "hud_transparent_note": "背景は完全透明で、速度計の線と体力バーだけを描画します。ウィンドウはドラッグできます。",
        "telemetry_not_generated_title": "HUD data note",
        "telemetry_not_generated_body": "通常キャンペーンで ems/danyria_hud_telemetry.txt が生成されない場合、この環境では addon の VScript が自動読み込みされていません。外部 HUD だけではゲーム内速度や体力を取得できません。",
    },
    "ko": {
        "hud_windows_title": "HUD 창 설정",
        "hud_settings_hint": "속도계와 체력 표시를 두 개의 투명 창으로 분리했습니다. 저장 후 외부 HUD를 다시 시작하세요.",
        "speed_window": "속도계 창",
        "enemy_window": "체력 창",
        "hud_x": "X",
        "hud_y": "Y",
        "hud_scale": "크기",
        "hud_opacity": "불투명도",
        "hud_max_speed": "속도계 최대값",
        "hud_max_enemies": "최대 적 체력바 수",
        "hud_save_settings": "HUD 설정 저장",
        "hud_reset_settings": "HUD 설정 초기화",
        "hud_settings_saved": "HUD 설정이 저장되었습니다. 외부 HUD를 다시 시작하면 적용됩니다.",
        "hud_settings_reset": "HUD 설정이 초기화되었습니다. 외부 HUD를 다시 시작하면 적용됩니다.",
        "hud_transparent_note": "배경은 완전히 투명하며 속도계 선과 체력바만 표시됩니다. 창은 드래그할 수 있습니다.",
        "telemetry_not_generated_title": "일반 캠페인 텔레메트리 안내",
        "telemetry_not_generated_body": "일반 캠페인에서 ems/danyria_hud_telemetry.txt가 생성되지 않으면 addon의 VScript가 자동 로드되지 않는 환경입니다. 외부 HUD만으로 게임 속도/체력 데이터를 만들 수는 없습니다.",
    },
    "ru": {
        "hud_windows_title": "Настройки окон HUD",
        "hud_settings_hint": "Спидометр и здоровье теперь отдельные прозрачные окна. Сохраните настройки и перезапустите внешний HUD.",
        "speed_window": "Окно спидометра",
        "enemy_window": "Окно здоровья",
        "hud_x": "X",
        "hud_y": "Y",
        "hud_scale": "Масштаб",
        "hud_opacity": "Непрозрачность",
        "hud_max_speed": "Максимум спидометра",
        "hud_max_enemies": "Макс. полос врагов",
        "hud_save_settings": "Сохранить HUD",
        "hud_reset_settings": "Сбросить HUD",
        "hud_settings_saved": "Настройки HUD сохранены. Перезапустите внешний HUD.",
        "hud_settings_reset": "Настройки HUD сброшены. Перезапустите внешний HUD.",
        "hud_transparent_note": "Фон полностью прозрачный; рисуются только линии спидометра и полосы здоровья. Окна можно перетаскивать.",
        "telemetry_not_generated_title": "Телеметрия в обычной кампании",
        "telemetry_not_generated_body": "Если обычная кампания не создаёт ems/danyria_hud_telemetry.txt, значит addon VScript не загружается автоматически. Внешний HUD не может получить скорость/здоровье без игрового скрипта, addon или серверного плагина.",
    },
    "de": {
        "hud_windows_title": "HUD-Fenstereinstellungen",
        "hud_settings_hint": "Tacho und Gesundheitsanzeige sind jetzt getrennte transparente Fenster. Speichern und externes HUD neu starten.",
        "speed_window": "Tacho-Fenster",
        "enemy_window": "Gesundheits-Fenster",
        "hud_x": "X",
        "hud_y": "Y",
        "hud_scale": "Skalierung",
        "hud_opacity": "Deckkraft",
        "hud_max_speed": "Tacho-Maximum",
        "hud_max_enemies": "Max. Gegnerbalken",
        "hud_save_settings": "HUD-Einstellungen speichern",
        "hud_reset_settings": "HUD-Einstellungen zurücksetzen",
        "hud_settings_saved": "HUD-Einstellungen gespeichert. Externes HUD neu starten.",
        "hud_settings_reset": "HUD-Einstellungen zurückgesetzt. Externes HUD neu starten.",
        "hud_transparent_note": "Der Hintergrund ist vollständig transparent; nur Tacho-Linien und Gesundheitsbalken werden gezeichnet. Fenster sind ziehbar.",
        "telemetry_not_generated_title": "Telemetrie in normalen Kampagnen",
        "telemetry_not_generated_body": "Wenn normale Kampagnen keine ems/danyria_hud_telemetry.txt erzeugen, lädt L4D2 das Addon-VScript hier nicht automatisch. Das externe HUD braucht Daten von Spielskript, addon oder Server-Plugin.",
    },
    "fr": {
        "hud_windows_title": "Réglages des fenêtres HUD",
        "hud_settings_hint": "Le compteur et les barres de vie sont deux fenêtres transparentes séparées. Enregistrez puis relancez le HUD externe.",
        "speed_window": "Fenêtre du compteur",
        "enemy_window": "Fenêtre de vie",
        "hud_x": "X",
        "hud_y": "Y",
        "hud_scale": "Échelle",
        "hud_opacity": "Opacité",
        "hud_max_speed": "Vitesse max du compteur",
        "hud_max_enemies": "Barres ennemies max",
        "hud_save_settings": "Enregistrer le HUD",
        "hud_reset_settings": "Réinitialiser le HUD",
        "hud_settings_saved": "Réglages HUD enregistrés. Relancez le HUD externe.",
        "hud_settings_reset": "Réglages HUD réinitialisés. Relancez le HUD externe.",
        "hud_transparent_note": "Le fond est totalement transparent ; seules les lignes du compteur et les barres de vie sont dessinées. Les fenêtres sont déplaçables.",
        "telemetry_not_generated_title": "Télémétrie en campagne normale",
        "telemetry_not_generated_body": "Si la campagne normale ne génère pas ems/danyria_hud_telemetry.txt, L4D2 ne charge pas automatiquement le VScript de l’addon. Le HUD externe a besoin d’un script, d’une addon ou d’un plugin serveur.",
    },
    "es": {
        "hud_windows_title": "Ajustes de ventanas HUD",
        "hud_settings_hint": "El velocímetro y la salud son dos ventanas transparentes separadas. Guarda y reinicia el HUD externo.",
        "speed_window": "Ventana del velocímetro",
        "enemy_window": "Ventana de salud",
        "hud_x": "X",
        "hud_y": "Y",
        "hud_scale": "Escala",
        "hud_opacity": "Opacidad",
        "hud_max_speed": "Máximo del velocímetro",
        "hud_max_enemies": "Máx. barras de enemigos",
        "hud_save_settings": "Guardar ajustes HUD",
        "hud_reset_settings": "Restablecer ajustes HUD",
        "hud_settings_saved": "Ajustes HUD guardados. Reinicia el HUD externo.",
        "hud_settings_reset": "Ajustes HUD restablecidos. Reinicia el HUD externo.",
        "hud_transparent_note": "El fondo es totalmente transparente; solo se dibujan líneas y barras. Las ventanas se pueden arrastrar.",
        "telemetry_not_generated_title": "Telemetría en campaña normal",
        "telemetry_not_generated_body": "Si una campaña normal no genera ems/danyria_hud_telemetry.txt, L4D2 no está cargando automáticamente el VScript del addon. El HUD externo necesita datos de script, addon o plugin de servidor.",
    },
}
for _lang, _extra in I18N_HUD_SPLIT.items():
    if _lang in I18N:
        I18N[_lang].update(_extra)

I18N_MUTATION_LAUNCHER = {
    "zh": {
        "launch_hud_test_campaign": "",
        "hud_test_campaign_hint": "",
        "hud_plugin_install_vpk_success": "HUD 遥测插件已安装。",
        "hud_plugin_install_folder_success": "HUD 遥测插件已安装。",
        "vpk_pack_failed": "插件安装已完成。",
        "launch_hud_test_failed": "失败",
        "launch_hud_test_missing_exe": "没有找到 left4dead2.exe。请确认路径是 left4dead2 文件夹。",
    },
    "en": {
        "launch_hud_test_campaign": "",
        "hud_test_campaign_hint": "",
        "hud_plugin_install_vpk_success": "HUD 遥测插件已安装。",
        "hud_plugin_install_folder_success": "HUD 遥测插件已安装。",
        "vpk_pack_failed": "Plugin installation is complete.",
        "launch_hud_test_failed": "Launch failed",
        "launch_hud_test_missing_exe": "left4dead2.exe was not found. Make sure the selected path is the left4dead2 folder.",
    },
    "ja": {
        "launch_hud_test_campaign": "",
        "hud_test_campaign_hint": "",
        "hud_plugin_install_vpk_success": "HUD telemetry plugin installed.",
        "hud_plugin_install_folder_success": "HUD telemetry plugin installed.",
        "vpk_pack_failed": "プラグインのインストールが完了しました。",
        "launch_hud_test_failed": "HUD テストキャンペーンの起動に失敗",
        "launch_hud_test_missing_exe": "left4dead2.exe が見つかりません。left4dead2 フォルダーを選択してください。",
    },
}
for _lang, _extra in I18N_MUTATION_LAUNCHER.items():
    if _lang in I18N:
        I18N[_lang].update(_extra)


I18N_MUTATION_LAUNCHER_COMPLETE = {
    "ko": {
        "launch_hud_test_campaign": "",
        "hud_test_campaign_hint": "",
        "hud_plugin_install_vpk_success": "HUD telemetry plugin installed.",
        "hud_plugin_install_folder_success": "HUD telemetry plugin installed.",
        "vpk_pack_failed": "플러그인 설치가 완료되었습니다.",
        "launch_hud_test_failed": "HUD 테스트 캠페인 시작 실패",
        "launch_hud_test_missing_exe": "left4dead2.exe를 찾을 수 없습니다. 선택한 경로가 left4dead2 폴더인지 확인하세요.",
    },
    "ru": {
        "launch_hud_test_campaign": "",
        "hud_test_campaign_hint": "",
        "hud_plugin_install_vpk_success": "HUD telemetry plugin installed.",
        "hud_plugin_install_folder_success": "HUD telemetry plugin installed.",
        "vpk_pack_failed": "Установка плагина завершена.",
        "launch_hud_test_failed": "Не удалось запустить тест HUD",
        "launch_hud_test_missing_exe": "left4dead2.exe не найден. Убедитесь, что выбран путь к папке left4dead2.",
    },
    "de": {
        "launch_hud_test_campaign": "",
        "hud_test_campaign_hint": "",
        "hud_plugin_install_vpk_success": "HUD telemetry plugin installed.",
        "hud_plugin_install_folder_success": "HUD telemetry plugin installed.",
        "vpk_pack_failed": "Plugin-Installation abgeschlossen.",
        "launch_hud_test_failed": "HUD-Testkampagne konnte nicht gestartet werden",
        "launch_hud_test_missing_exe": "left4dead2.exe wurde nicht gefunden. Prüfe, ob der gewählte Pfad der left4dead2-Ordner ist.",
    },
    "fr": {
        "launch_hud_test_campaign": "",
        "hud_test_campaign_hint": "",
        "hud_plugin_install_vpk_success": "HUD telemetry plugin installed.",
        "hud_plugin_install_folder_success": "HUD telemetry plugin installed.",
        "vpk_pack_failed": "Installation du plugin terminée.",
        "launch_hud_test_failed": "Échec du lancement de la campagne test HUD",
        "launch_hud_test_missing_exe": "left4dead2.exe est introuvable. Vérifiez que le chemin choisi est le dossier left4dead2.",
    },
    "es": {
        "launch_hud_test_campaign": "",
        "hud_test_campaign_hint": "",
        "hud_plugin_install_vpk_success": "HUD telemetry plugin installed.",
        "hud_plugin_install_folder_success": "HUD telemetry plugin installed.",
        "vpk_pack_failed": "Instalación del plugin completada.",
        "launch_hud_test_failed": "No se pudo iniciar la campaña de prueba HUD",
        "launch_hud_test_missing_exe": "No se encontró left4dead2.exe. Confirma que la ruta seleccionada sea la carpeta left4dead2.",
    },
}
for _lang, _extra in I18N_MUTATION_LAUNCHER_COMPLETE.items():
    if _lang in I18N:
        I18N[_lang].update(_extra)

I18N_RESPONSIVE_UI = {
    "zh": {
        "hud_enemy_distance": "敌人最大距离",
        "hud_responsive_note": "响应优化：HUD 读取频率和脚本写出频率提高；血条会过滤距离过远的敌人，减少误判。",
    },
    "en": {
        "hud_enemy_distance": "Enemy max distance",
        "hud_responsive_note": "Responsiveness improved: faster HUD polling and faster telemetry writes; distant enemies are filtered to reduce false positives.",
    },
    "ja": {
        "hud_enemy_distance": "敵の最大距離",
        "hud_responsive_note": "応答性を改善：HUD 読み取りとテレメトリ書き出しを高速化し、遠すぎる敵を除外します。",
    },
    "ko": {
        "hud_enemy_distance": "적 최대 거리",
        "hud_responsive_note": "응답성 개선: HUD 읽기와 텔레메트리 쓰기 속도를 높이고, 너무 먼 적은 제외합니다.",
    },
    "ru": {
        "hud_enemy_distance": "Макс. дистанция врагов",
        "hud_responsive_note": "Отклик улучшен: HUD быстрее читает данные, телеметрия пишет чаще, дальние враги фильтруются.",
    },
    "de": {
        "hud_enemy_distance": "Max. Gegnerdistanz",
        "hud_responsive_note": "Reaktionszeit verbessert: schnelleres Lesen und Schreiben; entfernte Gegner werden gefiltert.",
    },
    "fr": {
        "hud_enemy_distance": "Distance max ennemis",
        "hud_responsive_note": "Réactivité améliorée : lecture et écriture plus rapides ; les ennemis trop éloignés sont filtrés.",
    },
    "es": {
        "hud_enemy_distance": "Distancia máxima de enemigos",
        "hud_responsive_note": "Respuesta mejorada: lectura y escritura más rápidas; se filtran enemigos demasiado lejanos.",
    },
}
for _lang, _extra in I18N_RESPONSIVE_UI.items():
    if _lang in I18N:
        I18N[_lang].update(_extra)







I18N_PENALTY_PLUGIN = {
    "zh": {
        "plugin_penalty_title": "评分系统插件",
        "plugin_penalty_subtitle": "统计倒地、死亡、救援、治疗、击杀、伤害输出、物资使用等行为，并用独立 HUD 展示评分。",
        "penalty_mechanism": "行为评分与全局状态",
        "penalty_mechanism_desc": "实时读取玩家自己的受伤、倒地/死亡、救援、治疗、击杀、伤害输出和物资使用，生成个人参考评分。它只是调试/娱乐机制，不会直接修改游戏规则。",
        "penalty_window": "评分 HUD",
        "install_penalty_plugin": "安装 / 更新评分系统插件",
        "launch_penalty_test_campaign": "",
        "penalty_plugin_status": "评分插件状态",
        "penalty_plugin_desc": "游戏内脚本负责输出评分统计；外置 HUD 会新增评分系统卡片。",
        "penalty_launch_hint": "",
        "penalty_plugin_installed": "评分插件：已发现 {n} 项",
        "penalty_plugin_missing": "评分插件：未安装",
        "penalty_plugin_unknown": "评分插件：未确认",
        "missing_penalty_plugin_payload": "payload 中没有找到 danyria_penalty_plugin。",
        "penalty_plugin_install_success": "Score system plugin installed.",
        "penalty_plugin_install_failed": "评分系统插件安装失败",
        "penalty_plugin_install_vpk_success": "评分系统插件已安装。",
        "penalty_plugin_install_folder_success": "评分系统插件已安装。",
        "launch_penalty_test_failed": "启动失败",
        "hud_penalty_title": "评分系统",
        "hud_team_line": "队伍 {alive} 存活 / {incap} 倒地 / {dead} 死亡",
        "hud_enable_penalty": "启用评分 HUD",
        "hud_heal": "治疗",
        "hud_defib": "电击",
        "hud_kill": "击杀",
        "hud_common": "普感",
        "hud_special": "特感",
        "hud_witch": "女巫",
        "hud_tank": "Tank",
        "hud_protect": "保护",
        "hud_damage_taken": "受伤",
        "hud_damage_done": "伤害输出",
        "hud_items": "物资"
    },
    "en": {
        "plugin_penalty_title": "Score system plugin",
        "plugin_penalty_subtitle": "Tracks friendly fire, incaps, deaths, rescues, heals, kills, item usage with a dedicated HUD card.",
        "penalty_mechanism": "Behavior score and global state",
        "penalty_mechanism_desc": "Reads friendly fire, damage taken, incaps/deaths, revives, heals, kills, teammate item usage to produce a 0-100 reference score. It is a debug/entertainment layer and does not change game rules.",
        "penalty_window": "Score HUD",
        "install_penalty_plugin": "Install / Update Score System Plugin",
        "launch_penalty_test_campaign": "",
        "penalty_plugin_status": "Score plugin status",
        "penalty_plugin_desc": "The in-game script writes score stats; the external HUD adds a score-system card window.",
        "penalty_launch_hint": "",
        "penalty_plugin_installed": "Score plugin: found {n}",
        "penalty_plugin_missing": "Score plugin: not installed",
        "penalty_plugin_unknown": "Score plugin: unknown",
        "missing_penalty_plugin_payload": "danyria_penalty_plugin was not found in payload.",
        "penalty_plugin_install_success": "Score system plugin installed.",
        "penalty_plugin_install_failed": "Score system plugin install failed",
        "penalty_plugin_install_vpk_success": "评分系统插件已安装。",
        "penalty_plugin_install_folder_success": "评分系统插件已安装。",
        "launch_penalty_test_failed": "Launch failed",
        "hud_penalty_title": "SCORE SYSTEM",
        "hud_team_line": "TEAM {alive} alive / {incap} incap / {dead} dead",
        "hud_enable_penalty": "Enable score HUD",
        "hud_heal": "HEAL",
        "hud_defib": "DEFIB",
        "hud_kill": "KILL",
        "hud_common": "CI",
        "hud_special": "SI",
        "hud_witch": "WITCH",
        "hud_tank": "TANK",
        "hud_protect": "GUARD",
        "hud_damage_taken": "DMG-",
        "hud_damage_done": "DMG OUT",
        "hud_items": "ITEM"
    },
    "ja": {
        "plugin_penalty_title": "スコアシステムプラグイン",
        "plugin_penalty_subtitle": "味方撃ち、行動不能、死亡、蘇生、治療、撃破、救助、アイテム使用を集計し、専用 HUD に表示します。",
        "penalty_mechanism": "行動スコアと全体状態",
        "penalty_mechanism_desc": "味方撃ち、被ダメージ、行動不能/死亡、蘇生、治療、撃破、仲間の救助、アイテム使用から 0-100 の参考スコアを生成します。サーバールールは変更しません。",
        "penalty_window": "スコア HUD",
        "install_penalty_plugin": "スコアシステムをインストール / 更新",
        "launch_penalty_test_campaign": "",
        "penalty_plugin_status": "スコア状態",
        "penalty_plugin_desc": "ゲーム内スクリプトがスコア統計を出力し、外部 HUD が専用カードを表示します。",
        "penalty_launch_hint": "",
        "penalty_plugin_installed": "スコア：{n} 件",
        "penalty_plugin_missing": "スコア：未インストール",
        "penalty_plugin_unknown": "スコア：未確認",
        "missing_penalty_plugin_payload": "payload に danyria_penalty_plugin がありません。",
        "penalty_plugin_install_success": "Score system plugin installed.",
        "penalty_plugin_install_failed": "スコアシステムのインストールに失敗",
        "penalty_plugin_install_vpk_success": "Score system plugin installed.",
        "penalty_plugin_install_folder_success": "Score system plugin installed.",
        "launch_penalty_test_failed": "スコアテストの起動に失敗",
        "hud_penalty_title": "スコアシステム",
        "hud_team_line": "チーム {alive} 生存 / {incap} 行動不能 / {dead} 死亡",
        "hud_enable_penalty": "スコア HUD を有効化",
        "hud_heal": "治療",
        "hud_defib": "AED",
        "hud_kill": "撃破",
        "hud_common": "通常",
        "hud_special": "特殊",
        "hud_witch": "WITCH",
        "hud_tank": "TANK",
        "hud_protect": "保護",
        "hud_damage_taken": "被DMG",
        "hud_damage_done": "与ダメ",
        "hud_items": "物資"
    },
    "ko": {
        "plugin_penalty_title": "점수 시스템 플러그인",
        "plugin_penalty_subtitle": "아군 피해, 다운, 사망, 구조, 치료, 처치, 보호, 아이템 사용을 집계하고 전용 HUD에 표시합니다.",
        "penalty_mechanism": "행동 점수와 전역 상태",
        "penalty_mechanism_desc": "아군 피해, 받은 피해, 다운/사망, 구조, 치료, 처치, 팀원 보호, 아이템 사용으로 0-100 참고 점수를 만듭니다. 서버 규칙은 바꾸지 않습니다.",
        "penalty_window": "점수 HUD",
        "install_penalty_plugin": "점수 시스템 설치 / 업데이트",
        "launch_penalty_test_campaign": "",
        "penalty_plugin_status": "점수 플러그인 상태",
        "penalty_plugin_desc": "게임 스크립트가 점수 통계를 쓰고 외부 HUD가 별도 카드를 표시합니다.",
        "penalty_launch_hint": "",
        "penalty_plugin_installed": "점수: {n}개 발견",
        "penalty_plugin_missing": "점수: 미설치",
        "penalty_plugin_unknown": "점수: 미확인",
        "missing_penalty_plugin_payload": "payload에서 danyria_penalty_plugin을 찾을 수 없습니다.",
        "penalty_plugin_install_success": "Score system plugin installed.",
        "penalty_plugin_install_failed": "점수 시스템 설치 실패",
        "penalty_plugin_install_vpk_success": "Score system plugin installed.",
        "penalty_plugin_install_folder_success": "Score system plugin installed.",
        "launch_penalty_test_failed": "점수 테스트 시작 실패",
        "hud_penalty_title": "점수 시스템",
        "hud_team_line": "팀 {alive} 생존 / {incap} 다운 / {dead} 사망",
        "hud_enable_penalty": "점수 HUD 사용",
        "hud_heal": "회복",
        "hud_defib": "제세동",
        "hud_kill": "처치",
        "hud_common": "일좀",
        "hud_special": "특좀",
        "hud_witch": "WITCH",
        "hud_tank": "TANK",
        "hud_protect": "보호",
        "hud_damage_taken": "피해",
        "hud_damage_done": "가한피해",
        "hud_items": "물자"
    },
    "ru": {
        "plugin_penalty_title": "Плагин системы оценки",
        "plugin_penalty_subtitle": "Считает огонь по своим, ранения, смерти, спасения, лечение, убийства, защиту и предметы с отдельным HUD.",
        "penalty_mechanism": "Оценка поведения и общее состояние",
        "penalty_mechanism_desc": "Учитывает огонь по своим, полученный урон, падения/смерти, спасения, лечение, убийства, защиту союзников и предметы, формируя счёт 0-100. Правила сервера не меняются.",
        "penalty_window": "HUD оценки",
        "install_penalty_plugin": "Установить / обновить систему оценки",
        "launch_penalty_test_campaign": "",
        "penalty_plugin_status": "Состояние плагина оценки",
        "penalty_plugin_desc": "Игровой скрипт пишет статистику оценки; внешний HUD показывает отдельную карточку.",
        "penalty_launch_hint": "",
        "penalty_plugin_installed": "Плагин оценки: найдено {n}",
        "penalty_plugin_missing": "Плагин оценки: не установлен",
        "penalty_plugin_unknown": "Плагин оценки: неизвестно",
        "missing_penalty_plugin_payload": "В payload нет danyria_penalty_plugin.",
        "penalty_plugin_install_success": "Score system plugin installed.",
        "penalty_plugin_install_failed": "Ошибка установки системы оценки",
        "penalty_plugin_install_vpk_success": "Score system plugin installed.",
        "penalty_plugin_install_folder_success": "Score system plugin installed.",
        "launch_penalty_test_failed": "Ошибка запуска теста оценки",
        "hud_penalty_title": "СИСТЕМА ОЦЕНКИ",
        "hud_team_line": "КОМАНДА {alive} живы / {incap} упали / {dead} мертвы",
        "hud_enable_penalty": "Включить HUD оценки",
        "hud_heal": "HEAL",
        "hud_defib": "ДЕФИБ",
        "hud_kill": "УБИЙ.",
        "hud_common": "ОБЫЧ.",
        "hud_special": "ОСОБ.",
        "hud_witch": "WITCH",
        "hud_tank": "TANK",
        "hud_protect": "ЗАЩ.",
        "hud_damage_taken": "УРОН-",
        "hud_damage_done": "УРОН+",
        "hud_items": "ПРЕД."
    },
    "de": {
        "plugin_penalty_title": "Punktesystem-Plugin",
        "plugin_penalty_subtitle": "Erfasst Friendly Fire, Incaps, Tode, Revives, Heilung, Kills, Schutz und Items mit eigenem HUD.",
        "penalty_mechanism": "Verhaltenswertung und globaler Zustand",
        "penalty_mechanism_desc": "Wertet Friendly Fire, erlittenen Schaden, Incaps/Tode, Revives, Heilung, Kills, Schutz und Items zu einem Referenzwert von 0-100. Serverregeln werden nicht geändert.",
        "penalty_window": "Wertungs-HUD",
        "install_penalty_plugin": "Punktesystem installieren / aktualisieren",
        "launch_penalty_test_campaign": "",
        "penalty_plugin_status": "Punktesystem-Status",
        "penalty_plugin_desc": "Das Spielskript schreibt Wertungsstatistiken; das externe HUD zeigt eine eigene Karte.",
        "penalty_launch_hint": "",
        "penalty_plugin_installed": "Punktesystem: {n} gefunden",
        "penalty_plugin_missing": "Punktesystem: nicht installiert",
        "penalty_plugin_unknown": "Punktesystem: unbekannt",
        "missing_penalty_plugin_payload": "danyria_penalty_plugin fehlt im payload.",
        "penalty_plugin_install_success": "Score system plugin installed.",
        "penalty_plugin_install_failed": "Installation des Punktesystems fehlgeschlagen",
        "penalty_plugin_install_vpk_success": "Score system plugin installed.",
        "penalty_plugin_install_folder_success": "Score system plugin installed.",
        "launch_penalty_test_failed": "Wertungstest konnte nicht gestartet werden",
        "hud_penalty_title": "PUNKTESYSTEM",
        "hud_team_line": "TEAM {alive} lebt / {incap} down / {dead} tot",
        "hud_enable_penalty": "Wertungs-HUD aktivieren",
        "hud_heal": "HEAL",
        "hud_defib": "DEFIB",
        "hud_kill": "KILL",
        "hud_common": "CI",
        "hud_special": "SI",
        "hud_witch": "WITCH",
        "hud_tank": "TANK",
        "hud_protect": "SCHUTZ",
        "hud_damage_taken": "DMG-",
        "hud_damage_done": "DMG OUT",
        "hud_items": "ITEM"
    },
    "fr": {
        "plugin_penalty_title": "Plugin de système de score",
        "plugin_penalty_subtitle": "Suit tir allié, incapacitations, morts, secours, soins, éliminations, protection et objets avec un HUD dédié.",
        "penalty_mechanism": "Score de comportement et état global",
        "penalty_mechanism_desc": "Lit tir allié, dégâts subis, incapacitations/morts, secours, soins, éliminations, protection et objets pour produire un score 0-100. Les règles serveur ne changent pas.",
        "penalty_window": "HUD de score",
        "install_penalty_plugin": "Installer / mettre à jour le score",
        "launch_penalty_test_campaign": "",
        "penalty_plugin_status": "État du plugin de score",
        "penalty_plugin_desc": "Le script en jeu écrit les statistiques de score; le HUD externe affiche une carte dédiée.",
        "penalty_launch_hint": "",
        "penalty_plugin_installed": "Plugin de score : {n} trouvé(s)",
        "penalty_plugin_missing": "Plugin de score : non installé",
        "penalty_plugin_unknown": "Plugin de score : inconnu",
        "missing_penalty_plugin_payload": "danyria_penalty_plugin est absent du payload.",
        "penalty_plugin_install_success": "Score system plugin installed.",
        "penalty_plugin_install_failed": "Échec d’installation du système de score",
        "penalty_plugin_install_vpk_success": "Score system plugin installed.",
        "penalty_plugin_install_folder_success": "Score system plugin installed.",
        "launch_penalty_test_failed": "Échec du lancement du test score",
        "hud_penalty_title": "SYSTÈME DE SCORE",
        "hud_team_line": "ÉQUIPE {alive} vivants / {incap} incap. / {dead} morts",
        "hud_enable_penalty": "Activer le HUD de score",
        "hud_heal": "HEAL",
        "hud_defib": "DÉFIB",
        "hud_kill": "KILL",
        "hud_common": "CI",
        "hud_special": "SI",
        "hud_witch": "WITCH",
        "hud_tank": "TANK",
        "hud_protect": "GARDE",
        "hud_damage_taken": "DMG-",
        "hud_damage_done": "DÉGÂTS+",
        "hud_items": "OBJET"
    },
    "es": {
        "plugin_penalty_title": "Plugin de sistema de puntuación",
        "plugin_penalty_subtitle": "Registra fuego amigo, incapacitados, muertes, rescates, curas, bajas, protección y objetos con HUD propio.",
        "penalty_mechanism": "Puntuación de conducta y estado global",
        "penalty_mechanism_desc": "Lee fuego amigo, daño recibido, incapacitados/muertes, rescates, curas, bajas, protección y objetos para producir una puntuación 0-100. No cambia reglas del servidor.",
        "penalty_window": "HUD de puntuación",
        "install_penalty_plugin": "Instalar / actualizar sistema de puntuación",
        "launch_penalty_test_campaign": "",
        "penalty_plugin_status": "Estado del plugin de puntuación",
        "penalty_plugin_desc": "El script del juego escribe estadísticas de puntuación; el HUD externo añade una tarjeta separada.",
        "penalty_launch_hint": "",
        "penalty_plugin_installed": "Plugin de puntuación: {n} encontrado(s)",
        "penalty_plugin_missing": "Plugin de puntuación: no instalado",
        "penalty_plugin_unknown": "Plugin de puntuación: desconocido",
        "missing_penalty_plugin_payload": "No se encontró danyria_penalty_plugin en payload.",
        "penalty_plugin_install_success": "Score system plugin installed.",
        "penalty_plugin_install_failed": "Error al instalar sistema de puntuación",
        "penalty_plugin_install_vpk_success": "Score system plugin installed.",
        "penalty_plugin_install_folder_success": "Score system plugin installed.",
        "launch_penalty_test_failed": "Error al iniciar prueba de puntuación",
        "hud_penalty_title": "SISTEMA DE PUNTUACIÓN",
        "hud_team_line": "EQUIPO {alive} vivos / {incap} incap. / {dead} muertos",
        "hud_enable_penalty": "Activar HUD de puntuación",
        "hud_heal": "HEAL",
        "hud_defib": "DESFIB",
        "hud_kill": "BAJA",
        "hud_common": "CI",
        "hud_special": "SI",
        "hud_witch": "WITCH",
        "hud_tank": "TANK",
        "hud_protect": "PROT.",
        "hud_damage_taken": "DAÑO-",
        "hud_damage_done": "DAÑO+",
        "hud_items": "OBJ."
    }
}
for _lang, _extra in I18N_PENALTY_PLUGIN.items():
    if _lang in I18N:
        I18N[_lang].update(_extra)


I18N_SCORE_STRICT = {
    "zh": {"hud_ledge": "挂边", "hud_items": "物资", "hud_grade_ex_desc": "极致表现", "hud_grade_s_desc": "卓越表现", "hud_grade_a_desc": "优秀表现", "hud_grade_b_desc": "稳定表现", "hud_grade_c_desc": "勉强合格", "hud_grade_d_desc": "需要改进"},
    "en": {"hud_ledge": "LEDGE", "hud_items": "SUPPLY", "hud_grade_ex_desc": "Exceptional", "hud_grade_s_desc": "Superior", "hud_grade_a_desc": "Excellent", "hud_grade_b_desc": "Stable", "hud_grade_c_desc": "Passing", "hud_grade_d_desc": "Needs work"},
    "ja": {"hud_ledge": "崖掴み", "hud_items": "物資", "hud_grade_ex_desc": "極限評価", "hud_grade_s_desc": "卓越", "hud_grade_a_desc": "優秀", "hud_grade_b_desc": "安定", "hud_grade_c_desc": "合格圏", "hud_grade_d_desc": "要改善"},
    "ko": {"hud_ledge": "난간", "hud_items": "물자", "hud_grade_ex_desc": "최상", "hud_grade_s_desc": "탁월", "hud_grade_a_desc": "우수", "hud_grade_b_desc": "안정", "hud_grade_c_desc": "합격권", "hud_grade_d_desc": "개선 필요"},
    "ru": {"hud_ledge": "УСТУП", "hud_items": "ЗАПАСЫ", "hud_grade_ex_desc": "Исключительно", "hud_grade_s_desc": "Превосходно", "hud_grade_a_desc": "Отлично", "hud_grade_b_desc": "Стабильно", "hud_grade_c_desc": "Приемлемо", "hud_grade_d_desc": "Нужно лучше"},
    "de": {"hud_ledge": "KANTE", "hud_items": "VORRAT", "hud_grade_ex_desc": "Ausnahme", "hud_grade_s_desc": "Überragend", "hud_grade_a_desc": "Sehr gut", "hud_grade_b_desc": "Stabil", "hud_grade_c_desc": "Ausreichend", "hud_grade_d_desc": "Verbessern"},
    "fr": {"hud_ledge": "REBORD", "hud_items": "RESS.", "hud_grade_ex_desc": "Exceptionnel", "hud_grade_s_desc": "Supérieur", "hud_grade_a_desc": "Excellent", "hud_grade_b_desc": "Stable", "hud_grade_c_desc": "Passable", "hud_grade_d_desc": "À améliorer"},
    "es": {"hud_ledge": "BORDE", "hud_items": "SUMIN.", "hud_grade_ex_desc": "Excepcional", "hud_grade_s_desc": "Superior", "hud_grade_a_desc": "Excelente", "hud_grade_b_desc": "Estable", "hud_grade_c_desc": "Aceptable", "hud_grade_d_desc": "Mejorable"},
}
for _lang, _extra in I18N_SCORE_STRICT.items():
    if _lang in I18N:
        I18N[_lang].update(_extra)


I18N_PLUGIN_FOLDER_ONLY = {
    "zh": {
        "delete_hud_plugin": "删除 HUD 遥测插件",
        "delete_penalty_plugin": "删除评分系统插件",
        "hud_plugin_install_folder_success": "HUD telemetry plugin installed.",
        "penalty_plugin_install_folder_success": "Score system plugin installed.",
        "hud_plugin_delete_success": "HUD 遥测插件已删除，共清理 {n} 项。",
        "hud_plugin_delete_missing": "没有找到已安装的 HUD 遥测插件。",
        "hud_plugin_delete_failed": "HUD 遥测插件删除失败",
        "penalty_plugin_delete_success": "评分系统插件已删除，共清理 {n} 项。",
        "penalty_plugin_delete_missing": "没有找到已安装的评分系统插件。",
        "penalty_plugin_delete_failed": "评分系统插件删除失败",
    },
    "en": {
        "delete_hud_plugin": "Delete HUD Telemetry Plugin",
        "delete_penalty_plugin": "Delete Score System Plugin",
        "hud_plugin_install_folder_success": "HUD telemetry plugin installed.",
        "penalty_plugin_install_folder_success": "Score system plugin installed.",
        "hud_plugin_delete_success": "HUD telemetry plugin deleted. Cleaned {n} item(s).",
        "hud_plugin_delete_missing": "No installed HUD telemetry plugin was found.",
        "hud_plugin_delete_failed": "Failed to delete HUD telemetry plugin",
        "penalty_plugin_delete_success": "Score system plugin deleted. Cleaned {n} item(s).",
        "penalty_plugin_delete_missing": "No installed score system plugin was found.",
        "penalty_plugin_delete_failed": "Failed to delete score system plugin",
    },
    "ja": {
        "delete_hud_plugin": "HUD テレメトリを削除",
        "delete_penalty_plugin": "スコアシステムを削除",
        "hud_plugin_install_folder_success": "HUD telemetry plugin installed.",
        "penalty_plugin_install_folder_success": "Score system plugin installed.",
        "hud_plugin_delete_success": "HUD テレメトリを削除しました。{n} 件を清理しました。",
        "hud_plugin_delete_missing": "インストール済みの HUD テレメトリは見つかりません。",
        "hud_plugin_delete_failed": "HUD テレメトリの削除に失敗",
        "penalty_plugin_delete_success": "スコアシステムを削除しました。{n} 件を清理しました。",
        "penalty_plugin_delete_missing": "インストール済みのスコアシステムは見つかりません。",
        "penalty_plugin_delete_failed": "スコアシステムの削除に失敗",
    },
    "ko": {
        "delete_hud_plugin": "HUD 텔레메트리 삭제",
        "delete_penalty_plugin": "점수 시스템 삭제",
        "hud_plugin_install_folder_success": "HUD telemetry plugin installed.",
        "penalty_plugin_install_folder_success": "Score system plugin installed.",
        "hud_plugin_delete_success": "HUD 텔레메트리 플러그인을 삭제했습니다. {n}개 항목 정리됨.",
        "hud_plugin_delete_missing": "설치된 HUD 텔레메트리 플러그인을 찾지 못했습니다.",
        "hud_plugin_delete_failed": "HUD 텔레메트리 삭제 실패",
        "penalty_plugin_delete_success": "점수 시스템 플러그인을 삭제했습니다. {n}개 항목 정리됨.",
        "penalty_plugin_delete_missing": "설치된 점수 시스템 플러그인을 찾지 못했습니다.",
        "penalty_plugin_delete_failed": "점수 시스템 삭제 실패",
    },
    "ru": {
        "delete_hud_plugin": "Удалить HUD-телеметрию",
        "delete_penalty_plugin": "Удалить систему оценки",
        "hud_plugin_install_folder_success": "HUD telemetry plugin installed.",
        "penalty_plugin_install_folder_success": "Score system plugin installed.",
        "hud_plugin_delete_success": "HUD-телеметрия удалена. Очищено: {n}.",
        "hud_plugin_delete_missing": "Установленная HUD-телеметрия не найдена.",
        "hud_plugin_delete_failed": "Не удалось удалить HUD-телеметрию",
        "penalty_plugin_delete_success": "Система оценки удалена. Очищено: {n}.",
        "penalty_plugin_delete_missing": "Установленная система оценки не найдена.",
        "penalty_plugin_delete_failed": "Не удалось удалить систему оценки",
    },
    "de": {
        "delete_hud_plugin": "HUD-Telemetrie löschen",
        "delete_penalty_plugin": "Punktesystem löschen",
        "hud_plugin_install_folder_success": "HUD telemetry plugin installed.",
        "penalty_plugin_install_folder_success": "Score system plugin installed.",
        "hud_plugin_delete_success": "HUD-Telemetrie gelöscht. {n} Element(e) bereinigt.",
        "hud_plugin_delete_missing": "Keine installierte HUD-Telemetrie gefunden.",
        "hud_plugin_delete_failed": "HUD-Telemetrie konnte nicht gelöscht werden",
        "penalty_plugin_delete_success": "Punktesystem gelöscht. {n} Element(e) bereinigt.",
        "penalty_plugin_delete_missing": "Kein installiertes Punktesystem gefunden.",
        "penalty_plugin_delete_failed": "Punktesystem konnte nicht gelöscht werden",
    },
    "fr": {
        "delete_hud_plugin": "Supprimer la télémétrie HUD",
        "delete_penalty_plugin": "Supprimer le score",
        "hud_plugin_install_folder_success": "HUD telemetry plugin installed.",
        "penalty_plugin_install_folder_success": "Score system plugin installed.",
        "hud_plugin_delete_success": "Télémétrie HUD supprimée. {n} élément(s) nettoyé(s).",
        "hud_plugin_delete_missing": "Aucune télémétrie HUD installée trouvée.",
        "hud_plugin_delete_failed": "Échec de suppression de la télémétrie HUD",
        "penalty_plugin_delete_success": "Système de score supprimé. {n} élément(s) nettoyé(s).",
        "penalty_plugin_delete_missing": "Aucun système de score installé trouvé.",
        "penalty_plugin_delete_failed": "Échec de suppression du score",
    },
    "es": {
        "delete_hud_plugin": "Eliminar telemetría HUD",
        "delete_penalty_plugin": "Eliminar sistema de puntuación",
        "hud_plugin_install_folder_success": "HUD telemetry plugin installed.",
        "penalty_plugin_install_folder_success": "Score system plugin installed.",
        "hud_plugin_delete_success": "Telemetría HUD eliminada. {n} elemento(s) limpiado(s).",
        "hud_plugin_delete_missing": "No se encontró telemetría HUD instalada.",
        "hud_plugin_delete_failed": "Error al eliminar telemetría HUD",
        "penalty_plugin_delete_success": "Sistema de puntuación eliminado. {n} elemento(s) limpiado(s).",
        "penalty_plugin_delete_missing": "No se encontró sistema de puntuación instalado.",
        "penalty_plugin_delete_failed": "Error al eliminar sistema de puntuación",
    },
}
for _lang, _extra in I18N_PLUGIN_FOLDER_ONLY.items():
    if _lang in I18N:
        I18N[_lang].update(_extra)

_i18n_base_keys = set(I18N[I18N_BASE].keys())
_i18n_missing = {lang: sorted(_i18n_base_keys - set(data.keys())) for lang, data in I18N.items()}
if any(_i18n_missing.values()):
    raise RuntimeError(f"I18N missing keys: {_i18n_missing}")

# ---------------------------------------------------------------------------
# 武器数值编辑器文本。放在 I18N 完整性检查之后，其他语言会自动回退中文。
# Weapon editor strings. Added after I18N validation so other languages fall back to Chinese.
# ---------------------------------------------------------------------------
I18N_WEAPON_EDITOR = {'zh': {'version_label': '版本',
        'page_weapons': '武器工坊',
        'weapon_panel_title': '拆包区',
        'weapon_panel_hint': '只列出官方枪械和官方近战/特殊近战脚本；可从 pak01_dir.vpk、DLC、update、addons、workshop 自动拆出脚本。编辑后生成独立覆盖 VPK 放进 addons，不直接破坏原版包。',
        'weapon_scan': '扫描武器脚本',
        'weapon_unpack_vpk': '从 VPK 拆出脚本',
        'weapon_pack_vpk': '安装覆盖 VPK',
        'weapon_open_workspace': '打开工作区',
        'weapon_save': '保存当前武器',
        'weapon_reload': '重新载入',
        'weapon_open_scripts': '打开 scripts',
        'weapon_open_file': '打开当前文件',
        'weapon_list_title': '武器列表',
        'weapon_values_title': '数值修改',
        'weapon_perf_title': '参考性能',
        'weapon_summary_title': '当前武器',
        'weapon_metrics_title': '模拟数据',
        'weapon_top_rank_title': '',
        'weapon_search_placeholder': '搜索武器译名、英文名、文件名、参数名……',
        'weapon_col_rank': '',
        'weapon_col_name': '武器',
        'weapon_col_kind': '类型',
        'weapon_col_dps': '理论 DPS',
        'weapon_col_sustained': '持续 DPS',
        'weapon_col_burst': '1 秒爆发',
        'weapon_col_score': '评分',
        'weapon_param_key': '脚本字段',
        'weapon_param_label': '对应翻译',
        'weapon_param_value': '当前值',
        'weapon_param_original': '原值',
        'weapon_param_line': '行',
        'weapon_metric_name': '数据项',
        'weapon_metric_value': '数值',
        'weapon_kind_gun': '枪械',
        'weapon_kind_melee': '近战',
        'weapon_no_scripts_title': '没有找到武器脚本',
        'weapon_no_scripts_body': '没有找到官方武器脚本。请先点“从 VPK 拆出脚本”，或确认 left4dead2/scripts 与 left4dead2/scripts/melee 里有官方脚本。',
        'weapon_select_first': '请先选择一个武器。',
        'weapon_save_done': '已保存，并生成备份：\n{backup}',
        'weapon_save_failed': '保存武器数值失败',
        'weapon_invalid_number': '第 {row} 行不是合法数字：{value}',
        'weapon_perf_note': '参考模拟：只按脚本数值估算，不等于实战手感；MOD、难度倍率和命中率都会影响实际表现。',
        'weapon_metric_damage': '单发/单击伤害',
        'weapon_metric_cycle': '攻击间隔',
        'weapon_metric_clip': '弹匣/连击容量',
        'weapon_metric_reload': '换弹时间',
        'weapon_metric_accuracy': '稳定系数',
        'weapon_metric_score': '综合评分',
        'weapon_changed_hint': '已改动；保存后会写入工作区脚本，安装覆盖 VPK 后进游戏生效。',
        'weapon_not_changed': '当前武器没有改动。',
        'weapon_scanned': '已读取 {n} 个官方武器脚本',
        'weapon_source': '来源',
        'weapon_workspace': 'Danyria 工作区',
        'weapon_rel_path': '包内路径',
        'weapon_internal_name': '内部文件名',
        'weapon_vpk_extract_title': 'VPK 拆包',
        'weapon_vpk_extract_none': '没有在已扫描 VPK 里找到官方武器脚本。',
        'weapon_vpk_extract_done': '已从 {sources} 个 VPK 来源拆出 {files} 个官方武器脚本。\n工作区：{folder}',
        'weapon_vpk_pack_empty': '工作区没有可打包的官方武器脚本。请先从 VPK 拆出脚本。',
        'weapon_vpk_pack_title': '覆盖 VPK 已安装',
        'weapon_vpk_pack_done': '已生成并安装到：\n{path}',
        'weapon_vpk_pack_failed': '安装覆盖 VPK 失败',
        'weapon_param_generic': '脚本数值参数',
        'param_damage': '伤害',
        'param_damageperhit': '每次命中伤害',
        'param_bullets': '弹丸数',
        'param_pellets': '霰弹弹丸数',
        'param_cycletime': '射击/攻击间隔',
        'param_refiredelay': '再次开火延迟',
        'param_attackinterval': '攻击间隔',
        'param_swingtime': '挥击时间',
        'param_clipsize': '弹匣容量',
        'param_defaultclip': '默认弹药',
        'param_maxclip': '最大弹药',
        'param_reloadduration': '换弹时长',
        'param_reloadtime': '换弹时间',
        'param_reloademptyduration': '空仓换弹时长',
        'param_deployduration': '部署/掏出时长',
        'param_maxplayerspeed': '持武器移动速度',
        'param_weaponarmorratio': '护甲伤害比例',
        'param_verticalpunch': '垂直后坐',
        'param_punchangle': '后坐角度',
        'param_recoil': '后坐力',
        'param_spreadpershot': '每发扩散',
        'param_maxspread': '最大扩散',
        'param_spreaddecay': '扩散恢复',
        'param_minstandingspread': '站立最小扩散',
        'param_minduckingspread': '蹲下最小扩散',
        'param_mininairspread': '空中最小扩散',
        'param_maxmovementspread': '移动最大扩散',
        'param_aimingspread': '瞄准扩散',
        'param_range': '有效距离',
        'param_rangemodifier': '距离伤害系数',
        'param_swingrange': '挥砍距离',
        'param_crosshairmindistance': '准星最小距离',
        'param_crosshairdeltadistance': '准星变化距离',
        'param_penetrationnumlayers': '穿透层数',
        'param_penetrationpower': '穿透强度',
        'param_rumble': '手柄震动',
        'param_bucket': '武器槽',
        'param_bucketposition': '槽位位置',
        'param_tier': '物资等级',
        'param_weight': '权重',
        'param_itemflags': '物品标记',
        'param_damageflags': '伤害类型标记',
        'param_duration': '持续时间',
        'param_startdir': '挥击起始方向',
        'param_enddir': '挥击结束方向',
        'param_starttime': '判定开始时间',
        'param_endtime': '判定结束时间',
        'param_force': '击退力',
        'param_forcedir': '击退方向',
        'weapon_name_weapon_autoshotgun': '自动霰弹枪',
        'weapon_name_weapon_grenade_launcher': '榴弹发射器',
        'weapon_name_weapon_hunting_rifle': '猎枪',
        'weapon_name_weapon_pistol': '手枪',
        'weapon_name_weapon_pistol_magnum': '马格南手枪',
        'weapon_name_weapon_pumpshotgun': '泵动式霰弹枪',
        'weapon_name_weapon_rifle': 'M16 突击步枪',
        'weapon_name_weapon_rifle_ak47': 'AK-47 突击步枪',
        'weapon_name_weapon_rifle_desert': 'SCAR 战斗步枪',
        'weapon_name_weapon_rifle_m60': 'M60 机枪',
        'weapon_name_weapon_rifle_sg552': 'SG 552 步枪',
        'weapon_name_weapon_shotgun_chrome': '镀铬霰弹枪',
        'weapon_name_weapon_shotgun_spas': 'SPAS 战斗霰弹枪',
        'weapon_name_weapon_smg': '冲锋枪',
        'weapon_name_weapon_smg_mp5': 'MP5 冲锋枪',
        'weapon_name_weapon_smg_silenced': '消音冲锋枪',
        'weapon_name_weapon_sniper_awp': 'AWP 狙击步枪',
        'weapon_name_weapon_sniper_military': '军用狙击步枪',
        'weapon_name_weapon_sniper_scout': 'Scout 狙击步枪',
        'weapon_name_weapon_chainsaw': '电锯',
        'weapon_name_baseball_bat': '棒球棒',
        'weapon_name_cricket_bat': '板球拍',
        'weapon_name_crowbar': '撬棍',
        'weapon_name_electric_guitar': '电吉他',
        'weapon_name_fireaxe': '消防斧',
        'weapon_name_frying_pan': '平底锅',
        'weapon_name_golfclub': '高尔夫球杆',
        'weapon_name_katana': '武士刀',
        'weapon_name_knife': '匕首',
        'weapon_name_machete': '砍刀',
        'weapon_name_pitchfork': '干草叉',
        'weapon_name_shovel': '铲子',
        'weapon_name_tonfa': '警棍'},
 'en': {'version_label': 'VERSION',
        'page_weapons': 'Weapon Workshop',
        'weapon_panel_title': 'Unpack Area',
        'weapon_panel_hint': 'Only official firearm and official melee/special-melee scripts are listed. Scripts can be extracted from '
                             'pak01_dir.vpk, DLC, update, addons, and workshop VPKs. Edits are packed as a separate override VPK in addons '
                             'and do not overwrite the original packages.',
        'weapon_scan': 'Scan weapon scripts',
        'weapon_unpack_vpk': 'Extract from VPK',
        'weapon_pack_vpk': 'Install override VPK',
        'weapon_open_workspace': 'Open workspace',
        'weapon_save': 'Save current weapon',
        'weapon_reload': 'Reload',
        'weapon_open_scripts': 'Open scripts',
        'weapon_open_file': 'Open current file',
        'weapon_list_title': 'Weapon list',
        'weapon_values_title': 'Value Editing',
        'weapon_perf_title': 'Reference performance',
        'weapon_summary_title': 'Current weapon',
        'weapon_metrics_title': 'Simulation data',
        'weapon_top_rank_title': '',
        'weapon_search_placeholder': 'Search localized name, English name, file name, parameter name…',
        'weapon_col_rank': '',
        'weapon_col_name': 'Weapon',
        'weapon_col_kind': 'Type',
        'weapon_col_dps': 'Theoretical DPS',
        'weapon_col_sustained': 'Sustained DPS',
        'weapon_col_burst': '1s burst',
        'weapon_col_score': 'Score',
        'weapon_param_key': 'Script key',
        'weapon_param_label': 'Translation',
        'weapon_param_value': 'Current value',
        'weapon_param_original': 'Original',
        'weapon_param_line': 'Line',
        'weapon_metric_name': 'Metric',
        'weapon_metric_value': 'Value',
        'weapon_kind_gun': 'Firearm',
        'weapon_kind_melee': 'Melee',
        'weapon_no_scripts_title': 'No weapon scripts found',
        'weapon_no_scripts_body': 'No official weapon scripts were found. Use “Extract from VPK” first, or check left4dead2/scripts and '
                                  'left4dead2/scripts/melee.',
        'weapon_select_first': 'Select a weapon first.',
        'weapon_save_done': 'Saved and backup created:\n{backup}',
        'weapon_save_failed': 'Failed to save weapon values',
        'weapon_invalid_number': 'Row {row} is not a valid number: {value}',
        'weapon_perf_note': 'Reference simulation: estimated only from script values. Real combat feel can differ because of mods, '
                            'difficulty multipliers, and hit rate.',
        'weapon_metric_damage': 'Damage per shot/hit',
        'weapon_metric_cycle': 'Attack interval',
        'weapon_metric_clip': 'Magazine/combo capacity',
        'weapon_metric_reload': 'Reload time',
        'weapon_metric_accuracy': 'Stability factor',
        'weapon_metric_score': 'Overall score',
        'weapon_changed_hint': 'Changed. Save to write the workspace script; install the override VPK to apply it in game.',
        'weapon_not_changed': 'The current weapon has no changes.',
        'weapon_scanned': 'Loaded {n} official weapon scripts',
        'weapon_source': 'Source',
        'weapon_workspace': 'Danyria workspace',
        'weapon_rel_path': 'Package path',
        'weapon_internal_name': 'Internal file name',
        'weapon_vpk_extract_title': 'VPK extraction',
        'weapon_vpk_extract_none': 'No official weapon scripts were found in the scanned VPKs.',
        'weapon_vpk_extract_done': 'Extracted {files} official weapon scripts from {sources} VPK sources.\nWorkspace: {folder}',
        'weapon_vpk_pack_empty': 'The workspace has no official weapon scripts to pack. Extract from VPK first.',
        'weapon_vpk_pack_title': 'Override VPK installed',
        'weapon_vpk_pack_done': 'Generated and installed to:\n{path}',
        'weapon_vpk_pack_failed': 'Failed to install override VPK',
        'weapon_param_generic': 'Script numeric parameter',
        'param_damage': 'Damage',
        'param_damageperhit': 'Damage per hit',
        'param_bullets': 'Bullets',
        'param_pellets': 'Pellets',
        'param_cycletime': 'Fire/attack interval',
        'param_refiredelay': 'Refire delay',
        'param_attackinterval': 'Attack interval',
        'param_swingtime': 'Swing time',
        'param_clipsize': 'Magazine size',
        'param_defaultclip': 'Default ammo',
        'param_maxclip': 'Max ammo',
        'param_reloadduration': 'Reload duration',
        'param_reloadtime': 'Reload time',
        'param_reloademptyduration': 'Empty reload duration',
        'param_deployduration': 'Deploy duration',
        'param_maxplayerspeed': 'Move speed while held',
        'param_weaponarmorratio': 'Armor damage ratio',
        'param_verticalpunch': 'Vertical recoil',
        'param_punchangle': 'Recoil angle',
        'param_recoil': 'Recoil',
        'param_spreadpershot': 'Spread per shot',
        'param_maxspread': 'Maximum spread',
        'param_spreaddecay': 'Spread decay',
        'param_minstandingspread': 'Min standing spread',
        'param_minduckingspread': 'Min crouching spread',
        'param_mininairspread': 'Min airborne spread',
        'param_maxmovementspread': 'Max movement spread',
        'param_aimingspread': 'Aiming spread',
        'param_range': 'Range',
        'param_rangemodifier': 'Range damage modifier',
        'param_swingrange': 'Swing range',
        'param_crosshairmindistance': 'Crosshair min distance',
        'param_crosshairdeltadistance': 'Crosshair delta distance',
        'param_penetrationnumlayers': 'Penetration layers',
        'param_penetrationpower': 'Penetration power',
        'param_rumble': 'Controller rumble',
        'param_bucket': 'Weapon bucket',
        'param_bucketposition': 'Bucket position',
        'param_tier': 'Supply tier',
        'param_weight': 'Weight',
        'param_itemflags': 'Item flags',
        'param_damageflags': 'Damage type flags',
        'param_duration': 'Duration',
        'param_startdir': 'Swing start direction',
        'param_enddir': 'Swing end direction',
        'param_starttime': 'Hit start time',
        'param_endtime': 'Hit end time',
        'param_force': 'Force',
        'param_forcedir': 'Force direction',
        'weapon_name_weapon_autoshotgun': 'Auto Shotgun',
        'weapon_name_weapon_grenade_launcher': 'Grenade Launcher',
        'weapon_name_weapon_hunting_rifle': 'Hunting Rifle',
        'weapon_name_weapon_pistol': 'Pistol',
        'weapon_name_weapon_pistol_magnum': 'Magnum Pistol',
        'weapon_name_weapon_pumpshotgun': 'Pump Shotgun',
        'weapon_name_weapon_rifle': 'M16 Assault Rifle',
        'weapon_name_weapon_rifle_ak47': 'AK-47',
        'weapon_name_weapon_rifle_desert': 'Combat Rifle / SCAR',
        'weapon_name_weapon_rifle_m60': 'M60 Machine Gun',
        'weapon_name_weapon_rifle_sg552': 'SG 552',
        'weapon_name_weapon_shotgun_chrome': 'Chrome Shotgun',
        'weapon_name_weapon_shotgun_spas': 'SPAS Combat Shotgun',
        'weapon_name_weapon_smg': 'Submachine Gun',
        'weapon_name_weapon_smg_mp5': 'MP5',
        'weapon_name_weapon_smg_silenced': 'Silenced Submachine Gun',
        'weapon_name_weapon_sniper_awp': 'AWP Sniper Rifle',
        'weapon_name_weapon_sniper_military': 'Military Sniper Rifle',
        'weapon_name_weapon_sniper_scout': 'Scout Sniper Rifle',
        'weapon_name_weapon_chainsaw': 'Chainsaw',
        'weapon_name_baseball_bat': 'Baseball Bat',
        'weapon_name_cricket_bat': 'Cricket Bat',
        'weapon_name_crowbar': 'Crowbar',
        'weapon_name_electric_guitar': 'Electric Guitar',
        'weapon_name_fireaxe': 'Fire Axe',
        'weapon_name_frying_pan': 'Frying Pan',
        'weapon_name_golfclub': 'Golf Club',
        'weapon_name_katana': 'Katana',
        'weapon_name_knife': 'Knife',
        'weapon_name_machete': 'Machete',
        'weapon_name_pitchfork': 'Pitchfork',
        'weapon_name_shovel': 'Shovel',
        'weapon_name_tonfa': 'Tonfa / Nightstick'},
 'ja': {'version_label': 'バージョン',
        'page_weapons': '武器工房',
        'weapon_panel_title': '展開エリア',
        'weapon_panel_hint': '公式の銃火器と公式の近接/特殊近接スクリプトのみ表示します。pak01_dir.vpk、DLC、update、addons、workshop の VPK から抽出できます。編集内容は addons 内の独立した上書き '
                             'VPK として作成し、原本パッケージは上書きしません。',
        'weapon_scan': '武器スクリプトをスキャン',
        'weapon_unpack_vpk': 'VPK から抽出',
        'weapon_pack_vpk': '上書き VPK を導入',
        'weapon_open_workspace': '作業フォルダーを開く',
        'weapon_save': '現在の武器を保存',
        'weapon_reload': '再読み込み',
        'weapon_open_scripts': 'scripts を開く',
        'weapon_open_file': '現在のファイルを開く',
        'weapon_list_title': '武器一覧',
        'weapon_values_title': '数値変更',
        'weapon_perf_title': '参考性能 / ランキング',
        'weapon_summary_title': '現在の武器',
        'weapon_metrics_title': 'シミュレーションデータ',
        'weapon_top_rank_title': '',
        'weapon_search_placeholder': '翻訳名、英語名、ファイル名、パラメータ名を検索…',
        'weapon_col_rank': '',
        'weapon_col_name': '武器',
        'weapon_col_kind': '種類',
        'weapon_col_dps': '理論 DPS',
        'weapon_col_sustained': '継続 DPS',
        'weapon_col_burst': '1 秒バースト',
        'weapon_col_score': 'スコア',
        'weapon_param_key': 'スクリプト項目',
        'weapon_param_label': '翻訳',
        'weapon_param_value': '現在値',
        'weapon_param_original': '元の値',
        'weapon_param_line': '行',
        'weapon_metric_name': '項目',
        'weapon_metric_value': '値',
        'weapon_kind_gun': '銃火器',
        'weapon_kind_melee': '近接',
        'weapon_no_scripts_title': '武器スクリプトが見つかりません',
        'weapon_no_scripts_body': '公式武器スクリプトが見つかりません。「VPK から抽出」を先に実行するか、left4dead2/scripts と left4dead2/scripts/melee を確認してください。',
        'weapon_select_first': '先に武器を選択してください。',
        'weapon_save_done': '保存しました。バックアップ：\n{backup}',
        'weapon_save_failed': '武器数値の保存に失敗しました',
        'weapon_invalid_number': '{row} 行目は有効な数値ではありません：{value}',
        'weapon_perf_note': '参考シミュレーション：スクリプト数値のみから推定します。MOD、サーバープラグイン、難易度倍率、命中率により実戦感は変わります。',
        'weapon_metric_damage': '1 発/1 ヒットのダメージ',
        'weapon_metric_cycle': '攻撃間隔',
        'weapon_metric_clip': 'マガジン/コンボ容量',
        'weapon_metric_reload': 'リロード時間',
        'weapon_metric_accuracy': '安定係数',
        'weapon_metric_score': '総合スコア',
        'weapon_changed_hint': '変更済みです。保存すると作業スクリプトに書き込み、上書き VPK の導入後にゲームへ反映されます。',
        'weapon_not_changed': '現在の武器に変更はありません。',
        'weapon_scanned': '公式武器スクリプトを {n} 個読み込みました',
        'weapon_source': '出典',
        'weapon_workspace': 'Danyria 作業フォルダー',
        'weapon_rel_path': 'パッケージ内パス',
        'weapon_internal_name': '内部ファイル名',
        'weapon_vpk_extract_title': 'VPK 抽出',
        'weapon_vpk_extract_none': 'スキャンした VPK に公式武器スクリプトが見つかりません。',
        'weapon_vpk_extract_done': '{sources} 個の VPK 出典から公式武器スクリプトを {files} 個抽出しました。\n作業フォルダー：{folder}',
        'weapon_vpk_pack_empty': '作業フォルダーにパック可能な公式武器スクリプトがありません。先に VPK から抽出してください。',
        'weapon_vpk_pack_title': '上書き VPK を導入しました',
        'weapon_vpk_pack_done': '生成して導入しました：\n{path}',
        'weapon_vpk_pack_failed': '上書き VPK の導入に失敗しました',
        'weapon_param_generic': 'スクリプト数値パラメータ',
        'param_damage': 'ダメージ',
        'param_damageperhit': 'ヒットごとのダメージ',
        'param_bullets': '弾数',
        'param_pellets': 'ペレット数',
        'param_cycletime': '射撃/攻撃間隔',
        'param_refiredelay': '再射撃遅延',
        'param_attackinterval': '攻撃間隔',
        'param_swingtime': '振り時間',
        'param_clipsize': 'マガジン容量',
        'param_defaultclip': '初期弾薬',
        'param_maxclip': '最大弾薬',
        'param_reloadduration': 'リロード時間',
        'param_reloadtime': 'リロード時間',
        'param_reloademptyduration': '空マガジンリロード時間',
        'param_deployduration': '構え時間',
        'param_maxplayerspeed': '保持時移動速度',
        'param_weaponarmorratio': 'アーマーダメージ比',
        'param_verticalpunch': '垂直反動',
        'param_punchangle': '反動角度',
        'param_recoil': '反動',
        'param_spreadpershot': '発射ごとの拡散',
        'param_maxspread': '最大拡散',
        'param_spreaddecay': '拡散回復',
        'param_minstandingspread': '立ち最小拡散',
        'param_minduckingspread': 'しゃがみ最小拡散',
        'param_mininairspread': '空中最小拡散',
        'param_maxmovementspread': '移動最大拡散',
        'param_aimingspread': '照準拡散',
        'param_range': '射程',
        'param_rangemodifier': '距離ダメージ補正',
        'param_swingrange': '近接射程',
        'param_crosshairmindistance': 'クロスヘア最小距離',
        'param_crosshairdeltadistance': 'クロスヘア変化距離',
        'param_penetrationnumlayers': '貫通層数',
        'param_penetrationpower': '貫通力',
        'param_rumble': 'コントローラー振動',
        'param_bucket': '武器スロット',
        'param_bucketposition': 'スロット位置',
        'param_tier': '物資ランク',
        'param_weight': '重み',
        'param_itemflags': 'アイテムフラグ',
        'param_damageflags': 'ダメージ種別フラグ',
        'param_duration': '持続時間',
        'param_startdir': '振り開始方向',
        'param_enddir': '振り終了方向',
        'param_starttime': '判定開始時間',
        'param_endtime': '判定終了時間',
        'param_force': '力',
        'param_forcedir': '力の方向',
        'weapon_name_weapon_autoshotgun': 'オートショットガン',
        'weapon_name_weapon_grenade_launcher': 'グレネードランチャー',
        'weapon_name_weapon_hunting_rifle': 'ハンティングライフル',
        'weapon_name_weapon_pistol': 'ピストル',
        'weapon_name_weapon_pistol_magnum': 'マグナムピストル',
        'weapon_name_weapon_pumpshotgun': 'ポンプショットガン',
        'weapon_name_weapon_rifle': 'M16 アサルトライフル',
        'weapon_name_weapon_rifle_ak47': 'AK-47',
        'weapon_name_weapon_rifle_desert': 'コンバットライフル / SCAR',
        'weapon_name_weapon_rifle_m60': 'M60 機関銃',
        'weapon_name_weapon_rifle_sg552': 'SG 552',
        'weapon_name_weapon_shotgun_chrome': 'クロームショットガン',
        'weapon_name_weapon_shotgun_spas': 'SPAS コンバットショットガン',
        'weapon_name_weapon_smg': 'サブマシンガン',
        'weapon_name_weapon_smg_mp5': 'MP5',
        'weapon_name_weapon_smg_silenced': '消音サブマシンガン',
        'weapon_name_weapon_sniper_awp': 'AWP スナイパーライフル',
        'weapon_name_weapon_sniper_military': '軍用スナイパーライフル',
        'weapon_name_weapon_sniper_scout': 'Scout スナイパーライフル',
        'weapon_name_weapon_chainsaw': 'チェーンソー',
        'weapon_name_baseball_bat': '野球バット',
        'weapon_name_cricket_bat': 'クリケットバット',
        'weapon_name_crowbar': 'バール',
        'weapon_name_electric_guitar': 'エレキギター',
        'weapon_name_fireaxe': '消防斧',
        'weapon_name_frying_pan': 'フライパン',
        'weapon_name_golfclub': 'ゴルフクラブ',
        'weapon_name_katana': '刀',
        'weapon_name_knife': 'ナイフ',
        'weapon_name_machete': 'マチェット',
        'weapon_name_pitchfork': 'ピッチフォーク',
        'weapon_name_shovel': 'シャベル',
        'weapon_name_tonfa': 'トンファー / 警棒'},
 'ko': {'version_label': '버전',
        'page_weapons': '무기 공방',
        'weapon_panel_title': '추출 영역',
        'weapon_panel_hint': '공식 총기와 공식 근접/특수 근접 스크립트만 표시합니다. pak01_dir.vpk, DLC, update, addons, workshop VPK에서 추출할 수 있습니다. 수정 내용은 '
                             'addons의 독립 오버라이드 VPK로 만들며 원본 패키지를 덮어쓰지 않습니다.',
        'weapon_scan': '무기 스크립트 스캔',
        'weapon_unpack_vpk': 'VPK에서 추출',
        'weapon_pack_vpk': '오버라이드 VPK 설치',
        'weapon_open_workspace': '작업 폴더 열기',
        'weapon_save': '현재 무기 저장',
        'weapon_reload': '다시 불러오기',
        'weapon_open_scripts': 'scripts 열기',
        'weapon_open_file': '현재 파일 열기',
        'weapon_list_title': '무기 목록',
        'weapon_values_title': '수치 수정',
        'weapon_perf_title': '참고 성능 / 순위',
        'weapon_summary_title': '현재 무기',
        'weapon_metrics_title': '시뮬레이션 데이터',
        'weapon_top_rank_title': '',
        'weapon_search_placeholder': '번역명, 영어명, 파일명, 매개변수명 검색…',
        'weapon_col_rank': '',
        'weapon_col_name': '무기',
        'weapon_col_kind': '유형',
        'weapon_col_dps': '이론 DPS',
        'weapon_col_sustained': '지속 DPS',
        'weapon_col_burst': '1초 폭딜',
        'weapon_col_score': '점수',
        'weapon_param_key': '스크립트 키',
        'weapon_param_label': '번역',
        'weapon_param_value': '현재 값',
        'weapon_param_original': '원래 값',
        'weapon_param_line': '줄',
        'weapon_metric_name': '항목',
        'weapon_metric_value': '값',
        'weapon_kind_gun': '총기',
        'weapon_kind_melee': '근접',
        'weapon_no_scripts_title': '무기 스크립트를 찾을 수 없음',
        'weapon_no_scripts_body': '공식 무기 스크립트를 찾지 못했습니다. 먼저 “VPK에서 추출”을 누르거나 left4dead2/scripts 및 left4dead2/scripts/melee를 확인하세요.',
        'weapon_select_first': '먼저 무기를 선택하세요.',
        'weapon_save_done': '저장했고 백업을 만들었습니다:\n{backup}',
        'weapon_save_failed': '무기 수치 저장 실패',
        'weapon_invalid_number': '{row}행은 올바른 숫자가 아닙니다: {value}',
        'weapon_perf_note': '참고 시뮬레이션: 스크립트 수치만으로 추정합니다. MOD, 서버 플러그인, 난이도 배율, 명중률에 따라 실제 느낌은 달라질 수 있습니다.',
        'weapon_metric_damage': '발/타격당 피해',
        'weapon_metric_cycle': '공격 간격',
        'weapon_metric_clip': '탄창/콤보 용량',
        'weapon_metric_reload': '재장전 시간',
        'weapon_metric_accuracy': '안정 계수',
        'weapon_metric_score': '종합 점수',
        'weapon_changed_hint': '변경됨. 저장하면 작업 스크립트에 기록되고 오버라이드 VPK 설치 후 게임에 적용됩니다.',
        'weapon_not_changed': '현재 무기는 변경 사항이 없습니다.',
        'weapon_scanned': '공식 무기 스크립트 {n}개를 불러왔습니다',
        'weapon_source': '출처',
        'weapon_workspace': 'Danyria 작업 폴더',
        'weapon_rel_path': '패키지 경로',
        'weapon_internal_name': '내부 파일명',
        'weapon_vpk_extract_title': 'VPK 추출',
        'weapon_vpk_extract_none': '스캔한 VPK에서 공식 무기 스크립트를 찾지 못했습니다.',
        'weapon_vpk_extract_done': '{sources}개의 VPK 출처에서 공식 무기 스크립트 {files}개를 추출했습니다.\n작업 폴더: {folder}',
        'weapon_vpk_pack_empty': '작업 폴더에 패킹할 공식 무기 스크립트가 없습니다. 먼저 VPK에서 추출하세요.',
        'weapon_vpk_pack_title': '오버라이드 VPK 설치됨',
        'weapon_vpk_pack_done': '생성 및 설치 위치:\n{path}',
        'weapon_vpk_pack_failed': '오버라이드 VPK 설치 실패',
        'weapon_param_generic': '스크립트 숫자 매개변수',
        'param_damage': '피해',
        'param_damageperhit': '타격당 피해',
        'param_bullets': '탄환 수',
        'param_pellets': '펠릿 수',
        'param_cycletime': '사격/공격 간격',
        'param_refiredelay': '재발사 지연',
        'param_attackinterval': '공격 간격',
        'param_swingtime': '휘두르기 시간',
        'param_clipsize': '탄창 크기',
        'param_defaultclip': '기본 탄약',
        'param_maxclip': '최대 탄약',
        'param_reloadduration': '재장전 시간',
        'param_reloadtime': '재장전 시간',
        'param_reloademptyduration': '빈 탄창 재장전 시간',
        'param_deployduration': '꺼내는 시간',
        'param_maxplayerspeed': '소지 중 이동 속도',
        'param_weaponarmorratio': '방어구 피해 비율',
        'param_verticalpunch': '수직 반동',
        'param_punchangle': '반동 각도',
        'param_recoil': '반동',
        'param_spreadpershot': '발당 확산',
        'param_maxspread': '최대 확산',
        'param_spreaddecay': '확산 회복',
        'param_minstandingspread': '서 있을 때 최소 확산',
        'param_minduckingspread': '앉을 때 최소 확산',
        'param_mininairspread': '공중 최소 확산',
        'param_maxmovementspread': '이동 최대 확산',
        'param_aimingspread': '조준 확산',
        'param_range': '사거리',
        'param_rangemodifier': '거리 피해 보정',
        'param_swingrange': '근접 사거리',
        'param_crosshairmindistance': '조준점 최소 거리',
        'param_crosshairdeltadistance': '조준점 변화 거리',
        'param_penetrationnumlayers': '관통 층수',
        'param_penetrationpower': '관통력',
        'param_rumble': '컨트롤러 진동',
        'param_bucket': '무기 슬롯',
        'param_bucketposition': '슬롯 위치',
        'param_tier': '보급 등급',
        'param_weight': '가중치',
        'param_itemflags': '아이템 플래그',
        'param_damageflags': '피해 유형 플래그',
        'param_duration': '지속 시간',
        'param_startdir': '휘두르기 시작 방향',
        'param_enddir': '휘두르기 종료 방향',
        'param_starttime': '판정 시작 시간',
        'param_endtime': '판정 종료 시간',
        'param_force': '힘',
        'param_forcedir': '힘 방향',
        'weapon_name_weapon_autoshotgun': '자동 산탄총',
        'weapon_name_weapon_grenade_launcher': '유탄 발사기',
        'weapon_name_weapon_hunting_rifle': '헌팅 라이플',
        'weapon_name_weapon_pistol': '권총',
        'weapon_name_weapon_pistol_magnum': '매그넘 권총',
        'weapon_name_weapon_pumpshotgun': '펌프 산탄총',
        'weapon_name_weapon_rifle': 'M16 돌격소총',
        'weapon_name_weapon_rifle_ak47': 'AK-47',
        'weapon_name_weapon_rifle_desert': '전투 소총 / SCAR',
        'weapon_name_weapon_rifle_m60': 'M60 기관총',
        'weapon_name_weapon_rifle_sg552': 'SG 552',
        'weapon_name_weapon_shotgun_chrome': '크롬 산탄총',
        'weapon_name_weapon_shotgun_spas': 'SPAS 전투 산탄총',
        'weapon_name_weapon_smg': '기관단총',
        'weapon_name_weapon_smg_mp5': 'MP5',
        'weapon_name_weapon_smg_silenced': '소음 기관단총',
        'weapon_name_weapon_sniper_awp': 'AWP 저격소총',
        'weapon_name_weapon_sniper_military': '군용 저격소총',
        'weapon_name_weapon_sniper_scout': 'Scout 저격소총',
        'weapon_name_weapon_chainsaw': '전기톱',
        'weapon_name_baseball_bat': '야구 방망이',
        'weapon_name_cricket_bat': '크리켓 배트',
        'weapon_name_crowbar': '쇠지렛대',
        'weapon_name_electric_guitar': '일렉트릭 기타',
        'weapon_name_fireaxe': '소방 도끼',
        'weapon_name_frying_pan': '프라이팬',
        'weapon_name_golfclub': '골프채',
        'weapon_name_katana': '카타나',
        'weapon_name_knife': '칼',
        'weapon_name_machete': '마체테',
        'weapon_name_pitchfork': '쇠스랑',
        'weapon_name_shovel': '삽',
        'weapon_name_tonfa': '톤파 / 경찰봉'},
 'ru': {'version_label': 'ВЕРСИЯ',
        'page_weapons': 'Параметры оружия',
        'weapon_panel_title': 'Зона распаковки',
        'weapon_panel_hint': 'Показываются только официальные скрипты огнестрельного и ближнего/особого ближнего оружия. Скрипты можно '
                             'извлечь из pak01_dir.vpk, DLC, update, addons и workshop VPK. Изменения упаковываются как отдельный override '
                             'VPK в addons и не перезаписывают оригинальные пакеты.',
        'weapon_scan': 'Сканировать скрипты',
        'weapon_unpack_vpk': 'Извлечь из VPK',
        'weapon_pack_vpk': 'Установить override VPK',
        'weapon_open_workspace': 'Открыть рабочую папку',
        'weapon_save': 'Сохранить оружие',
        'weapon_reload': 'Перезагрузить',
        'weapon_open_scripts': 'Открыть scripts',
        'weapon_open_file': 'Открыть текущий файл',
        'weapon_list_title': 'Список оружия',
        'weapon_values_title': 'Изменение значений',
        'weapon_perf_title': 'Справочная эффективность / рейтинг',
        'weapon_summary_title': 'Текущее оружие',
        'weapon_metrics_title': 'Данные симуляции',
        'weapon_top_rank_title': '',
        'weapon_search_placeholder': 'Поиск по переводу, английскому названию, файлу, параметру…',
        'weapon_col_rank': '',
        'weapon_col_name': 'Оружие',
        'weapon_col_kind': 'Тип',
        'weapon_col_dps': 'Теор. DPS',
        'weapon_col_sustained': 'Уст. DPS',
        'weapon_col_burst': 'Урон за 1 с',
        'weapon_col_score': 'Оценка',
        'weapon_param_key': 'Ключ скрипта',
        'weapon_param_label': 'Перевод',
        'weapon_param_value': 'Текущее значение',
        'weapon_param_original': 'Исходное',
        'weapon_param_line': 'Строка',
        'weapon_metric_name': 'Показатель',
        'weapon_metric_value': 'Значение',
        'weapon_kind_gun': 'Огнестрельное',
        'weapon_kind_melee': 'Ближний бой',
        'weapon_no_scripts_title': 'Скрипты оружия не найдены',
        'weapon_no_scripts_body': 'Официальные скрипты оружия не найдены. Сначала используйте «Извлечь из VPK» или проверьте '
                                  'left4dead2/scripts и left4dead2/scripts/melee.',
        'weapon_select_first': 'Сначала выберите оружие.',
        'weapon_save_done': 'Сохранено, создана резервная копия:\n{backup}',
        'weapon_save_failed': 'Не удалось сохранить параметры оружия',
        'weapon_invalid_number': 'Строка {row}: недопустимое число: {value}',
        'weapon_perf_note': 'Справочная симуляция: оценка только по значениям скрипта. Реальное ощущение зависит от MOD, серверных '
                            'плагинов, множителей сложности и точности попаданий.',
        'weapon_metric_damage': 'Урон за выстрел/удар',
        'weapon_metric_cycle': 'Интервал атаки',
        'weapon_metric_clip': 'Магазин/комбо',
        'weapon_metric_reload': 'Время перезарядки',
        'weapon_metric_accuracy': 'Коэффициент стабильности',
        'weapon_metric_score': 'Общая оценка',
        'weapon_changed_hint': 'Изменено. Сохраните рабочий скрипт и установите override VPK для применения в игре.',
        'weapon_not_changed': 'У текущего оружия нет изменений.',
        'weapon_scanned': 'Загружено официальных скриптов оружия: {n}',
        'weapon_source': 'Источник',
        'weapon_workspace': 'Рабочая папка Danyria',
        'weapon_rel_path': 'Путь в пакете',
        'weapon_internal_name': 'Внутреннее имя файла',
        'weapon_vpk_extract_title': 'Извлечение VPK',
        'weapon_vpk_extract_none': 'В просканированных VPK не найдены официальные скрипты оружия.',
        'weapon_vpk_extract_done': 'Извлечено официальных скриптов: {files} из источников VPK: {sources}.\nРабочая папка: {folder}',
        'weapon_vpk_pack_empty': 'В рабочей папке нет официальных скриптов для упаковки. Сначала извлеките из VPK.',
        'weapon_vpk_pack_title': 'Override VPK установлен',
        'weapon_vpk_pack_done': 'Создано и установлено в:\n{path}',
        'weapon_vpk_pack_failed': 'Не удалось установить override VPK',
        'weapon_param_generic': 'Числовой параметр скрипта',
        'param_damage': 'Урон',
        'param_damageperhit': 'Урон за попадание',
        'param_bullets': 'Пули',
        'param_pellets': 'Дробины',
        'param_cycletime': 'Интервал выстрела/атаки',
        'param_refiredelay': 'Задержка повторного огня',
        'param_attackinterval': 'Интервал атаки',
        'param_swingtime': 'Время взмаха',
        'param_clipsize': 'Размер магазина',
        'param_defaultclip': 'Боезапас по умолчанию',
        'param_maxclip': 'Максимум патронов',
        'param_reloadduration': 'Длительность перезарядки',
        'param_reloadtime': 'Время перезарядки',
        'param_reloademptyduration': 'Перезарядка пустого магазина',
        'param_deployduration': 'Время доставания',
        'param_maxplayerspeed': 'Скорость с оружием',
        'param_weaponarmorratio': 'Коэфф. урона по броне',
        'param_verticalpunch': 'Вертикальная отдача',
        'param_punchangle': 'Угол отдачи',
        'param_recoil': 'Отдача',
        'param_spreadpershot': 'Разброс за выстрел',
        'param_maxspread': 'Макс. разброс',
        'param_spreaddecay': 'Снижение разброса',
        'param_minstandingspread': 'Мин. разброс стоя',
        'param_minduckingspread': 'Мин. разброс сидя',
        'param_mininairspread': 'Мин. разброс в воздухе',
        'param_maxmovementspread': 'Макс. разброс в движении',
        'param_aimingspread': 'Разброс при прицеливании',
        'param_range': 'Дальность',
        'param_rangemodifier': 'Модификатор урона от дистанции',
        'param_swingrange': 'Дальность удара',
        'param_crosshairmindistance': 'Мин. расстояние прицела',
        'param_crosshairdeltadistance': 'Изменение прицела',
        'param_penetrationnumlayers': 'Слои пробития',
        'param_penetrationpower': 'Сила пробития',
        'param_rumble': 'Вибрация контроллера',
        'param_bucket': 'Слот оружия',
        'param_bucketposition': 'Позиция слота',
        'param_tier': 'Уровень снабжения',
        'param_weight': 'Вес',
        'param_itemflags': 'Флаги предмета',
        'param_damageflags': 'Флаги типа урона',
        'param_duration': 'Длительность',
        'param_startdir': 'Начальное направление взмаха',
        'param_enddir': 'Конечное направление взмаха',
        'param_starttime': 'Начало хитбокса',
        'param_endtime': 'Конец хитбокса',
        'param_force': 'Сила',
        'param_forcedir': 'Направление силы',
        'weapon_name_weapon_autoshotgun': 'Автоматический дробовик',
        'weapon_name_weapon_grenade_launcher': 'Гранатомёт',
        'weapon_name_weapon_hunting_rifle': 'Охотничья винтовка',
        'weapon_name_weapon_pistol': 'Пистолет',
        'weapon_name_weapon_pistol_magnum': 'Пистолет «Магнум»',
        'weapon_name_weapon_pumpshotgun': 'Помповый дробовик',
        'weapon_name_weapon_rifle': 'Штурмовая винтовка M16',
        'weapon_name_weapon_rifle_ak47': 'AK-47',
        'weapon_name_weapon_rifle_desert': 'Боевая винтовка / SCAR',
        'weapon_name_weapon_rifle_m60': 'Пулемёт M60',
        'weapon_name_weapon_rifle_sg552': 'SG 552',
        'weapon_name_weapon_shotgun_chrome': 'Хромированный дробовик',
        'weapon_name_weapon_shotgun_spas': 'Боевой дробовик SPAS',
        'weapon_name_weapon_smg': 'Пистолет-пулемёт',
        'weapon_name_weapon_smg_mp5': 'MP5',
        'weapon_name_weapon_smg_silenced': 'ПП с глушителем',
        'weapon_name_weapon_sniper_awp': 'Снайперская винтовка AWP',
        'weapon_name_weapon_sniper_military': 'Военная снайперская винтовка',
        'weapon_name_weapon_sniper_scout': 'Снайперская винтовка Scout',
        'weapon_name_weapon_chainsaw': 'Бензопила',
        'weapon_name_baseball_bat': 'Бейсбольная бита',
        'weapon_name_cricket_bat': 'Крикетная бита',
        'weapon_name_crowbar': 'Лом',
        'weapon_name_electric_guitar': 'Электрогитара',
        'weapon_name_fireaxe': 'Пожарный топор',
        'weapon_name_frying_pan': 'Сковорода',
        'weapon_name_golfclub': 'Клюшка для гольфа',
        'weapon_name_katana': 'Катана',
        'weapon_name_knife': 'Нож',
        'weapon_name_machete': 'Мачете',
        'weapon_name_pitchfork': 'Вилы',
        'weapon_name_shovel': 'Лопата',
        'weapon_name_tonfa': 'Тонфа / дубинка'},
 'de': {'version_label': 'VERSION',
        'page_weapons': 'Waffenwerte',
        'weapon_panel_title': 'Entpackbereich',
        'weapon_panel_hint': 'Es werden nur offizielle Feuerwaffen- und offizielle Nahkampf-/Spezialnahkampf-Skripte angezeigt. Skripte '
                             'können aus pak01_dir.vpk, DLC, update, addons und workshop VPKs extrahiert werden. Änderungen werden als '
                             'separates Override-VPK in addons gepackt und überschreiben keine Originalpakete.',
        'weapon_scan': 'Waffenskripte scannen',
        'weapon_unpack_vpk': 'Aus VPK extrahieren',
        'weapon_pack_vpk': 'Override-VPK installieren',
        'weapon_open_workspace': 'Arbeitsordner öffnen',
        'weapon_save': 'Aktuelle Waffe speichern',
        'weapon_reload': 'Neu laden',
        'weapon_open_scripts': 'scripts öffnen',
        'weapon_open_file': 'Aktuelle Datei öffnen',
        'weapon_list_title': 'Waffenliste',
        'weapon_values_title': 'Werte bearbeiten',
        'weapon_perf_title': 'Referenzleistung',
        'weapon_summary_title': 'Aktuelle Waffe',
        'weapon_metrics_title': 'Simulationsdaten',
        'weapon_top_rank_title': '',
        'weapon_search_placeholder': 'Nach Übersetzung, englischem Namen, Datei oder Parameter suchen…',
        'weapon_col_rank': '',
        'weapon_col_name': 'Waffe',
        'weapon_col_kind': 'Typ',
        'weapon_col_dps': 'Theoretische DPS',
        'weapon_col_sustained': 'Dauer-DPS',
        'weapon_col_burst': '1s-Burst',
        'weapon_col_score': 'Wertung',
        'weapon_param_key': 'Skript-Schlüssel',
        'weapon_param_label': 'Übersetzung',
        'weapon_param_value': 'Aktueller Wert',
        'weapon_param_original': 'Original',
        'weapon_param_line': 'Zeile',
        'weapon_metric_name': 'Messwert',
        'weapon_metric_value': 'Wert',
        'weapon_kind_gun': 'Feuerwaffe',
        'weapon_kind_melee': 'Nahkampf',
        'weapon_no_scripts_title': 'Keine Waffenskripte gefunden',
        'weapon_no_scripts_body': 'Keine offiziellen Waffenskripte gefunden. Nutze zuerst „Aus VPK extrahieren“ oder prüfe '
                                  'left4dead2/scripts und left4dead2/scripts/melee.',
        'weapon_select_first': 'Wähle zuerst eine Waffe aus.',
        'weapon_save_done': 'Gespeichert und Backup erstellt:\n{backup}',
        'weapon_save_failed': 'Waffenwerte konnten nicht gespeichert werden',
        'weapon_invalid_number': 'Zeile {row} ist keine gültige Zahl: {value}',
        'weapon_perf_note': 'Referenzsimulation: nur aus Skriptwerten geschätzt. Mods, Server-Plugins, Schwierigkeitsmultiplikatoren und '
                            'Trefferquote können das echte Spielgefühl verändern.',
        'weapon_metric_damage': 'Schaden pro Schuss/Treffer',
        'weapon_metric_cycle': 'Angriffsintervall',
        'weapon_metric_clip': 'Magazin-/Kombokapazität',
        'weapon_metric_reload': 'Nachladezeit',
        'weapon_metric_accuracy': 'Stabilitätsfaktor',
        'weapon_metric_score': 'Gesamtwertung',
        'weapon_changed_hint': 'Geändert. Speichern schreibt das Arbeitsskript; installiere das Override-VPK für die Anwendung im Spiel.',
        'weapon_not_changed': 'Die aktuelle Waffe hat keine Änderungen.',
        'weapon_scanned': '{n} offizielle Waffenskripte geladen',
        'weapon_source': 'Quelle',
        'weapon_workspace': 'Danyria-Arbeitsordner',
        'weapon_rel_path': 'Paketpfad',
        'weapon_internal_name': 'Interner Dateiname',
        'weapon_vpk_extract_title': 'VPK-Extraktion',
        'weapon_vpk_extract_none': 'In den gescannten VPKs wurden keine offiziellen Waffenskripte gefunden.',
        'weapon_vpk_extract_done': '{files} offizielle Waffenskripte aus {sources} VPK-Quellen extrahiert.\nArbeitsordner: {folder}',
        'weapon_vpk_pack_empty': 'Im Arbeitsordner sind keine offiziellen Waffenskripte zum Packen. Erst aus VPK extrahieren.',
        'weapon_vpk_pack_title': 'Override-VPK installiert',
        'weapon_vpk_pack_done': 'Erzeugt und installiert nach:\n{path}',
        'weapon_vpk_pack_failed': 'Override-VPK konnte nicht installiert werden',
        'weapon_param_generic': 'Numerischer Skriptparameter',
        'param_damage': 'Schaden',
        'param_damageperhit': 'Schaden pro Treffer',
        'param_bullets': 'Kugeln',
        'param_pellets': 'Pellets',
        'param_cycletime': 'Feuer-/Angriffsintervall',
        'param_refiredelay': 'Nachfeuer-Verzögerung',
        'param_attackinterval': 'Angriffsintervall',
        'param_swingtime': 'Schwungzeit',
        'param_clipsize': 'Magazingröße',
        'param_defaultclip': 'Standardmunition',
        'param_maxclip': 'Maximale Munition',
        'param_reloadduration': 'Nachladedauer',
        'param_reloadtime': 'Nachladezeit',
        'param_reloademptyduration': 'Leernachladezeit',
        'param_deployduration': 'Ziehzeit',
        'param_maxplayerspeed': 'Bewegungsgeschwindigkeit',
        'param_weaponarmorratio': 'Rüstungsschadensfaktor',
        'param_verticalpunch': 'Vertikaler Rückstoß',
        'param_punchangle': 'Rückstoßwinkel',
        'param_recoil': 'Rückstoß',
        'param_spreadpershot': 'Streuung pro Schuss',
        'param_maxspread': 'Maximale Streuung',
        'param_spreaddecay': 'Streuungsabbau',
        'param_minstandingspread': 'Min. Streuung stehend',
        'param_minduckingspread': 'Min. Streuung geduckt',
        'param_mininairspread': 'Min. Streuung in der Luft',
        'param_maxmovementspread': 'Max. Bewegungsstreuung',
        'param_aimingspread': 'Zielstreuung',
        'param_range': 'Reichweite',
        'param_rangemodifier': 'Distanz-Schadensmodifikator',
        'param_swingrange': 'Schlagreichweite',
        'param_crosshairmindistance': 'Min. Fadenkreuzdistanz',
        'param_crosshairdeltadistance': 'Fadenkreuzänderung',
        'param_penetrationnumlayers': 'Durchdringungsschichten',
        'param_penetrationpower': 'Durchdringungskraft',
        'param_rumble': 'Controller-Vibration',
        'param_bucket': 'Waffenslot',
        'param_bucketposition': 'Slotposition',
        'param_tier': 'Versorgungsstufe',
        'param_weight': 'Gewicht',
        'param_itemflags': 'Gegenstands-Flags',
        'param_damageflags': 'Schadenstyp-Flags',
        'param_duration': 'Dauer',
        'param_startdir': 'Schwung-Start Richtung',
        'param_enddir': 'Schwung-Ende Richtung',
        'param_starttime': 'Trefferbeginn',
        'param_endtime': 'Trefferende',
        'param_force': 'Kraft',
        'param_forcedir': 'Kraftrichtung',
        'weapon_name_weapon_autoshotgun': 'Automatische Schrotflinte',
        'weapon_name_weapon_grenade_launcher': 'Granatwerfer',
        'weapon_name_weapon_hunting_rifle': 'Jagdgewehr',
        'weapon_name_weapon_pistol': 'Pistole',
        'weapon_name_weapon_pistol_magnum': 'Magnum-Pistole',
        'weapon_name_weapon_pumpshotgun': 'Pumpgun',
        'weapon_name_weapon_rifle': 'M16-Sturmgewehr',
        'weapon_name_weapon_rifle_ak47': 'AK-47',
        'weapon_name_weapon_rifle_desert': 'Kampfgewehr / SCAR',
        'weapon_name_weapon_rifle_m60': 'M60-Maschinengewehr',
        'weapon_name_weapon_rifle_sg552': 'SG 552',
        'weapon_name_weapon_shotgun_chrome': 'Chrome-Schrotflinte',
        'weapon_name_weapon_shotgun_spas': 'SPAS-Kampfschrotflinte',
        'weapon_name_weapon_smg': 'Maschinenpistole',
        'weapon_name_weapon_smg_mp5': 'MP5',
        'weapon_name_weapon_smg_silenced': 'Schallgedämpfte MP',
        'weapon_name_weapon_sniper_awp': 'AWP-Scharfschützengewehr',
        'weapon_name_weapon_sniper_military': 'Militär-Scharfschützengewehr',
        'weapon_name_weapon_sniper_scout': 'Scout-Scharfschützengewehr',
        'weapon_name_weapon_chainsaw': 'Kettensäge',
        'weapon_name_baseball_bat': 'Baseballschläger',
        'weapon_name_cricket_bat': 'Cricketschläger',
        'weapon_name_crowbar': 'Brecheisen',
        'weapon_name_electric_guitar': 'E-Gitarre',
        'weapon_name_fireaxe': 'Feuerwehraxt',
        'weapon_name_frying_pan': 'Bratpfanne',
        'weapon_name_golfclub': 'Golfschläger',
        'weapon_name_katana': 'Katana',
        'weapon_name_knife': 'Messer',
        'weapon_name_machete': 'Machete',
        'weapon_name_pitchfork': 'Heugabel',
        'weapon_name_shovel': 'Schaufel',
        'weapon_name_tonfa': 'Tonfa / Schlagstock'},
 'fr': {'version_label': 'VERSION',
        'page_weapons': 'Valeurs des armes',
        'weapon_panel_title': 'Zone d’extraction',
        'weapon_panel_hint': 'Seuls les scripts officiels d’armes à feu et de mêlée/mêlée spéciale sont affichés. Les scripts peuvent être '
                             'extraits de pak01_dir.vpk, DLC, update, addons et workshop. Les modifications sont empaquetées comme VPK de '
                             'remplacement séparé dans addons sans écraser les paquets originaux.',
        'weapon_scan': 'Scanner les scripts',
        'weapon_unpack_vpk': 'Extraire depuis VPK',
        'weapon_pack_vpk': 'Installer le VPK de remplacement',
        'weapon_open_workspace': 'Ouvrir l’espace de travail',
        'weapon_save': 'Enregistrer l’arme',
        'weapon_reload': 'Recharger',
        'weapon_open_scripts': 'Ouvrir scripts',
        'weapon_open_file': 'Ouvrir le fichier courant',
        'weapon_list_title': 'Liste des armes',
        'weapon_values_title': 'Modification des valeurs',
        'weapon_perf_title': 'Performance de référence / classement',
        'weapon_summary_title': 'Arme actuelle',
        'weapon_metrics_title': 'Données de simulation',
        'weapon_top_rank_title': '',
        'weapon_search_placeholder': 'Rechercher nom traduit, nom anglais, fichier, paramètre…',
        'weapon_col_rank': '',
        'weapon_col_name': 'Arme',
        'weapon_col_kind': 'Type',
        'weapon_col_dps': 'DPS théorique',
        'weapon_col_sustained': 'DPS soutenu',
        'weapon_col_burst': 'Burst 1 s',
        'weapon_col_score': 'Score',
        'weapon_param_key': 'Clé du script',
        'weapon_param_label': 'Traduction',
        'weapon_param_value': 'Valeur actuelle',
        'weapon_param_original': 'Original',
        'weapon_param_line': 'Ligne',
        'weapon_metric_name': 'Mesure',
        'weapon_metric_value': 'Valeur',
        'weapon_kind_gun': 'Arme à feu',
        'weapon_kind_melee': 'Mêlée',
        'weapon_no_scripts_title': 'Aucun script d’arme trouvé',
        'weapon_no_scripts_body': 'Aucun script officiel d’arme n’a été trouvé. Utilise d’abord « Extraire depuis VPK » ou vérifie '
                                  'left4dead2/scripts et left4dead2/scripts/melee.',
        'weapon_select_first': 'Sélectionne d’abord une arme.',
        'weapon_save_done': 'Enregistré, sauvegarde créée :\n{backup}',
        'weapon_save_failed': 'Échec de l’enregistrement des valeurs',
        'weapon_invalid_number': 'La ligne {row} n’est pas un nombre valide : {value}',
        'weapon_perf_note': 'Simulation de référence : estimation uniquement depuis les valeurs du script. Les mods, plugins serveur, '
                            'multiplicateurs de difficulté et la précision changent le ressenti réel.',
        'weapon_metric_damage': 'Dégâts par tir/coup',
        'weapon_metric_cycle': 'Intervalle d’attaque',
        'weapon_metric_clip': 'Chargeur/capacité combo',
        'weapon_metric_reload': 'Temps de rechargement',
        'weapon_metric_accuracy': 'Facteur de stabilité',
        'weapon_metric_score': 'Score global',
        'weapon_changed_hint': 'Modifié. Enregistre pour écrire le script de travail ; installe le VPK de remplacement pour l’appliquer en '
                               'jeu.',
        'weapon_not_changed': 'L’arme actuelle n’a pas été modifiée.',
        'weapon_scanned': '{n} scripts officiels d’armes chargés',
        'weapon_source': 'Source',
        'weapon_workspace': 'Espace de travail Danyria',
        'weapon_rel_path': 'Chemin dans le paquet',
        'weapon_internal_name': 'Nom de fichier interne',
        'weapon_vpk_extract_title': 'Extraction VPK',
        'weapon_vpk_extract_none': 'Aucun script officiel d’arme dans les VPK scannés.',
        'weapon_vpk_extract_done': '{files} scripts officiels extraits depuis {sources} sources VPK.\nEspace de travail : {folder}',
        'weapon_vpk_pack_empty': 'Aucun script officiel à empaqueter dans l’espace de travail. Extrais d’abord depuis VPK.',
        'weapon_vpk_pack_title': 'VPK de remplacement installé',
        'weapon_vpk_pack_done': 'Généré et installé dans :\n{path}',
        'weapon_vpk_pack_failed': 'Échec de l’installation du VPK de remplacement',
        'weapon_param_generic': 'Paramètre numérique du script',
        'param_damage': 'Dégâts',
        'param_damageperhit': 'Dégâts par coup',
        'param_bullets': 'Balles',
        'param_pellets': 'Plombs',
        'param_cycletime': 'Intervalle tir/attaque',
        'param_refiredelay': 'Délai de nouveau tir',
        'param_attackinterval': 'Intervalle d’attaque',
        'param_swingtime': 'Durée du swing',
        'param_clipsize': 'Taille du chargeur',
        'param_defaultclip': 'Munitions par défaut',
        'param_maxclip': 'Munitions max',
        'param_reloadduration': 'Durée de rechargement',
        'param_reloadtime': 'Temps de rechargement',
        'param_reloademptyduration': 'Rechargement à vide',
        'param_deployduration': 'Temps de déploiement',
        'param_maxplayerspeed': 'Vitesse avec l’arme',
        'param_weaponarmorratio': 'Ratio dégâts armure',
        'param_verticalpunch': 'Recul vertical',
        'param_punchangle': 'Angle de recul',
        'param_recoil': 'Recul',
        'param_spreadpershot': 'Dispersion par tir',
        'param_maxspread': 'Dispersion maximale',
        'param_spreaddecay': 'Récupération dispersion',
        'param_minstandingspread': 'Dispersion min debout',
        'param_minduckingspread': 'Dispersion min accroupi',
        'param_mininairspread': 'Dispersion min en l’air',
        'param_maxmovementspread': 'Dispersion max en mouvement',
        'param_aimingspread': 'Dispersion en visée',
        'param_range': 'Portée',
        'param_rangemodifier': 'Modificateur de dégâts à distance',
        'param_swingrange': 'Portée du coup',
        'param_crosshairmindistance': 'Distance min du réticule',
        'param_crosshairdeltadistance': 'Variation du réticule',
        'param_penetrationnumlayers': 'Couches de pénétration',
        'param_penetrationpower': 'Puissance de pénétration',
        'param_rumble': 'Vibration manette',
        'param_bucket': 'Emplacement d’arme',
        'param_bucketposition': 'Position d’emplacement',
        'param_tier': 'Niveau de ravitaillement',
        'param_weight': 'Poids',
        'param_itemflags': 'Drapeaux d’objet',
        'param_damageflags': 'Drapeaux de type de dégâts',
        'param_duration': 'Durée',
        'param_startdir': 'Direction de départ du swing',
        'param_enddir': 'Direction de fin du swing',
        'param_starttime': 'Début de détection',
        'param_endtime': 'Fin de détection',
        'param_force': 'Force',
        'param_forcedir': 'Direction de force',
        'weapon_name_weapon_autoshotgun': 'Fusil à pompe automatique',
        'weapon_name_weapon_grenade_launcher': 'Lance-grenades',
        'weapon_name_weapon_hunting_rifle': 'Fusil de chasse',
        'weapon_name_weapon_pistol': 'Pistolet',
        'weapon_name_weapon_pistol_magnum': 'Pistolet Magnum',
        'weapon_name_weapon_pumpshotgun': 'Fusil à pompe',
        'weapon_name_weapon_rifle': 'Fusil d’assaut M16',
        'weapon_name_weapon_rifle_ak47': 'AK-47',
        'weapon_name_weapon_rifle_desert': 'Fusil de combat / SCAR',
        'weapon_name_weapon_rifle_m60': 'Mitrailleuse M60',
        'weapon_name_weapon_rifle_sg552': 'SG 552',
        'weapon_name_weapon_shotgun_chrome': 'Fusil à pompe chromé',
        'weapon_name_weapon_shotgun_spas': 'Fusil de combat SPAS',
        'weapon_name_weapon_smg': 'Pistolet-mitrailleur',
        'weapon_name_weapon_smg_mp5': 'MP5',
        'weapon_name_weapon_smg_silenced': 'Pistolet-mitrailleur silencieux',
        'weapon_name_weapon_sniper_awp': 'Fusil de précision AWP',
        'weapon_name_weapon_sniper_military': 'Fusil de précision militaire',
        'weapon_name_weapon_sniper_scout': 'Fusil de précision Scout',
        'weapon_name_weapon_chainsaw': 'Tronçonneuse',
        'weapon_name_baseball_bat': 'Batte de baseball',
        'weapon_name_cricket_bat': 'Batte de cricket',
        'weapon_name_crowbar': 'Pied-de-biche',
        'weapon_name_electric_guitar': 'Guitare électrique',
        'weapon_name_fireaxe': 'Hache de pompier',
        'weapon_name_frying_pan': 'Poêle',
        'weapon_name_golfclub': 'Club de golf',
        'weapon_name_katana': 'Katana',
        'weapon_name_knife': 'Couteau',
        'weapon_name_machete': 'Machette',
        'weapon_name_pitchfork': 'Fourche',
        'weapon_name_shovel': 'Pelle',
        'weapon_name_tonfa': 'Tonfa / matraque'},
 'es': {'version_label': 'VERSIÓN',
        'page_weapons': 'Valores de armas',
        'weapon_panel_title': 'Zona de extracción',
        'weapon_panel_hint': 'Solo se muestran scripts oficiales de armas de fuego y de melee/melee especial. Los scripts pueden extraerse '
                             'de pak01_dir.vpk, DLC, update, addons y workshop. Los cambios se empaquetan como un VPK de reemplazo '
                             'independiente en addons sin sobrescribir paquetes originales.',
        'weapon_scan': 'Escanear scripts',
        'weapon_unpack_vpk': 'Extraer de VPK',
        'weapon_pack_vpk': 'Instalar VPK de reemplazo',
        'weapon_open_workspace': 'Abrir espacio de trabajo',
        'weapon_save': 'Guardar arma actual',
        'weapon_reload': 'Recargar',
        'weapon_open_scripts': 'Abrir scripts',
        'weapon_open_file': 'Abrir archivo actual',
        'weapon_list_title': 'Lista de armas',
        'weapon_values_title': 'Edición de valores',
        'weapon_perf_title': 'Rendimiento de referencia / clasificación',
        'weapon_summary_title': 'Arma actual',
        'weapon_metrics_title': 'Datos de simulación',
        'weapon_top_rank_title': '',
        'weapon_search_placeholder': 'Buscar nombre traducido, nombre inglés, archivo, parámetro…',
        'weapon_col_rank': '',
        'weapon_col_name': 'Arma',
        'weapon_col_kind': 'Tipo',
        'weapon_col_dps': 'DPS teórico',
        'weapon_col_sustained': 'DPS sostenido',
        'weapon_col_burst': 'Ráfaga 1 s',
        'weapon_col_score': 'Puntuación',
        'weapon_param_key': 'Clave de script',
        'weapon_param_label': 'Traducción',
        'weapon_param_value': 'Valor actual',
        'weapon_param_original': 'Original',
        'weapon_param_line': 'Línea',
        'weapon_metric_name': 'Métrica',
        'weapon_metric_value': 'Valor',
        'weapon_kind_gun': 'Arma de fuego',
        'weapon_kind_melee': 'Melee',
        'weapon_no_scripts_title': 'No se encontraron scripts de armas',
        'weapon_no_scripts_body': 'No se encontraron scripts oficiales de armas. Usa primero “Extraer de VPK” o revisa left4dead2/scripts '
                                  'y left4dead2/scripts/melee.',
        'weapon_select_first': 'Selecciona primero un arma.',
        'weapon_save_done': 'Guardado y copia creada:\n{backup}',
        'weapon_save_failed': 'No se pudieron guardar los valores',
        'weapon_invalid_number': 'La fila {row} no es un número válido: {value}',
        'weapon_perf_note': 'Simulación de referencia: estimada solo desde valores del script. Mods, plugins de servidor, multiplicadores '
                            'de dificultad y precisión pueden cambiar el resultado real.',
        'weapon_metric_damage': 'Daño por disparo/golpe',
        'weapon_metric_cycle': 'Intervalo de ataque',
        'weapon_metric_clip': 'Cargador/capacidad combo',
        'weapon_metric_reload': 'Tiempo de recarga',
        'weapon_metric_accuracy': 'Factor de estabilidad',
        'weapon_metric_score': 'Puntuación total',
        'weapon_changed_hint': 'Modificado. Guarda para escribir el script de trabajo; instala el VPK de reemplazo para aplicarlo en el '
                               'juego.',
        'weapon_not_changed': 'El arma actual no tiene cambios.',
        'weapon_scanned': '{n} scripts oficiales de armas cargados',
        'weapon_source': 'Fuente',
        'weapon_workspace': 'Espacio de trabajo Danyria',
        'weapon_rel_path': 'Ruta del paquete',
        'weapon_internal_name': 'Nombre interno de archivo',
        'weapon_vpk_extract_title': 'Extracción VPK',
        'weapon_vpk_extract_none': 'No se encontraron scripts oficiales de armas en los VPK escaneados.',
        'weapon_vpk_extract_done': 'Extraídos {files} scripts oficiales desde {sources} fuentes VPK.\nEspacio de trabajo: {folder}',
        'weapon_vpk_pack_empty': 'El espacio de trabajo no tiene scripts oficiales para empaquetar. Extrae primero desde VPK.',
        'weapon_vpk_pack_title': 'VPK de reemplazo instalado',
        'weapon_vpk_pack_done': 'Generado e instalado en:\n{path}',
        'weapon_vpk_pack_failed': 'Error al instalar el VPK de reemplazo',
        'weapon_param_generic': 'Parámetro numérico del script',
        'param_damage': 'Daño',
        'param_damageperhit': 'Daño por golpe',
        'param_bullets': 'Balas',
        'param_pellets': 'Perdigones',
        'param_cycletime': 'Intervalo de disparo/ataque',
        'param_refiredelay': 'Retraso de nuevo disparo',
        'param_attackinterval': 'Intervalo de ataque',
        'param_swingtime': 'Tiempo de swing',
        'param_clipsize': 'Tamaño del cargador',
        'param_defaultclip': 'Munición por defecto',
        'param_maxclip': 'Munición máxima',
        'param_reloadduration': 'Duración de recarga',
        'param_reloadtime': 'Tiempo de recarga',
        'param_reloademptyduration': 'Recarga en vacío',
        'param_deployduration': 'Tiempo de despliegue',
        'param_maxplayerspeed': 'Velocidad con el arma',
        'param_weaponarmorratio': 'Ratio de daño a armadura',
        'param_verticalpunch': 'Retroceso vertical',
        'param_punchangle': 'Ángulo de retroceso',
        'param_recoil': 'Retroceso',
        'param_spreadpershot': 'Dispersión por disparo',
        'param_maxspread': 'Dispersión máxima',
        'param_spreaddecay': 'Recuperación de dispersión',
        'param_minstandingspread': 'Dispersión mínima de pie',
        'param_minduckingspread': 'Dispersión mínima agachado',
        'param_mininairspread': 'Dispersión mínima en el aire',
        'param_maxmovementspread': 'Dispersión máxima en movimiento',
        'param_aimingspread': 'Dispersión al apuntar',
        'param_range': 'Alcance',
        'param_rangemodifier': 'Modificador de daño por distancia',
        'param_swingrange': 'Alcance del golpe',
        'param_crosshairmindistance': 'Distancia mínima de mira',
        'param_crosshairdeltadistance': 'Cambio de mira',
        'param_penetrationnumlayers': 'Capas de penetración',
        'param_penetrationpower': 'Potencia de penetración',
        'param_rumble': 'Vibración del mando',
        'param_bucket': 'Ranura de arma',
        'param_bucketposition': 'Posición de ranura',
        'param_tier': 'Nivel de suministro',
        'param_weight': 'Peso',
        'param_itemflags': 'Flags de objeto',
        'param_damageflags': 'Flags de tipo de daño',
        'param_duration': 'Duración',
        'param_startdir': 'Dirección inicial del swing',
        'param_enddir': 'Dirección final del swing',
        'param_starttime': 'Inicio de detección',
        'param_endtime': 'Fin de detección',
        'param_force': 'Fuerza',
        'param_forcedir': 'Dirección de fuerza',
        'weapon_name_weapon_autoshotgun': 'Escopeta automática',
        'weapon_name_weapon_grenade_launcher': 'Lanzagranadas',
        'weapon_name_weapon_hunting_rifle': 'Rifle de caza',
        'weapon_name_weapon_pistol': 'Pistola',
        'weapon_name_weapon_pistol_magnum': 'Pistola Magnum',
        'weapon_name_weapon_pumpshotgun': 'Escopeta de corredera',
        'weapon_name_weapon_rifle': 'Rifle de asalto M16',
        'weapon_name_weapon_rifle_ak47': 'AK-47',
        'weapon_name_weapon_rifle_desert': 'Rifle de combate / SCAR',
        'weapon_name_weapon_rifle_m60': 'Ametralladora M60',
        'weapon_name_weapon_rifle_sg552': 'SG 552',
        'weapon_name_weapon_shotgun_chrome': 'Escopeta cromada',
        'weapon_name_weapon_shotgun_spas': 'Escopeta de combate SPAS',
        'weapon_name_weapon_smg': 'Subfusil',
        'weapon_name_weapon_smg_mp5': 'MP5',
        'weapon_name_weapon_smg_silenced': 'Subfusil con silenciador',
        'weapon_name_weapon_sniper_awp': 'Rifle de francotirador AWP',
        'weapon_name_weapon_sniper_military': 'Rifle de francotirador militar',
        'weapon_name_weapon_sniper_scout': 'Rifle de francotirador Scout',
        'weapon_name_weapon_chainsaw': 'Motosierra',
        'weapon_name_baseball_bat': 'Bate de béisbol',
        'weapon_name_cricket_bat': 'Bate de críquet',
        'weapon_name_crowbar': 'Palanca',
        'weapon_name_electric_guitar': 'Guitarra eléctrica',
        'weapon_name_fireaxe': 'Hacha de bombero',
        'weapon_name_frying_pan': 'Sartén',
        'weapon_name_golfclub': 'Palo de golf',
        'weapon_name_katana': 'Katana',
        'weapon_name_knife': 'Cuchillo',
        'weapon_name_machete': 'Machete',
        'weapon_name_pitchfork': 'Horca',
        'weapon_name_shovel': 'Pala',
        'weapon_name_tonfa': 'Tonfa / porra'}}
for _lang, _extra in I18N_WEAPON_EDITOR.items():
    if _lang in I18N:
        I18N[_lang].update(_extra)

_i18n_final_keys = set(I18N[I18N_BASE].keys())
_i18n_final_missing = {lang: sorted(_i18n_final_keys - set(data.keys())) for lang, data in I18N.items()}
if any(_i18n_final_missing.values()):
    raise RuntimeError(f"I18N final missing keys: {_i18n_final_missing}")


# ---------------------------------------------------------------------------
# 外部语言包加载。assets/i18n.json 为主语言配置，内置表只作为缺失/损坏时的备用。
# External language-pack loader. assets/i18n.json is the primary language source;
# ---------------------------------------------------------------------------
def _merge_i18n_pack(base: dict, extra: dict) -> dict:
    merged = json.loads(json.dumps(base, ensure_ascii=False))
    if not isinstance(extra, dict):
        return merged
    for lang, data in extra.items():
        if not isinstance(data, dict):
            continue
        merged.setdefault(str(lang), {})
        for key, value in data.items():
            if isinstance(value, str):
                merged[str(lang)][str(key)] = value
    return merged


def _external_i18n_path() -> Path:
    return Path(__file__).resolve().parent / "assets" / "i18n.json"


def _load_external_i18n(base: dict) -> dict:
    try:
        p = _external_i18n_path()
        if p.exists():
            return _merge_i18n_pack(base, json.loads(p.read_text(encoding="utf-8")))
    except Exception:
        pass
    return base


I18N = _load_external_i18n(I18N)

# 插件页文字补丁。删除运行提示，并把评分系统标为测试项目。
# Plugin-page text patch. Removes launch hints and marks score system as test.
I18N_PLUGIN_TEXT_PATCH = {
    'zh': {'plugin_hud_title': 'Danyria 插件', 'plugin_hud_subtitle': '外置 HUD：速度表 + 敌人血量显示。', 'hud_plugin_status': 'Danyria 插件状态', 'hud_plugin_desc': 'Danyria 插件：写出速度、血量和敌人数据。', 'hud_launch_hint': '', 'hud_plugin_install_success': 'HUD 遥测插件已安装。', 'hud_plugin_install_vpk_success': 'HUD 遥测插件已安装。', 'hud_plugin_install_folder_success': 'HUD 遥测插件已安装。', 'plugin_penalty_title': '评分系统插件（测试项目）', 'plugin_penalty_subtitle': '测试项目：个人击杀、治疗、受伤、物资和输出统计 HUD。', 'penalty_plugin_desc': '评分系统测试插件：写出个人统计和评分数据。', 'penalty_mechanism_desc': '实时读取玩家自己的受伤、倒地/死亡、救援、治疗、击杀、伤害输出和物资使用，生成个人参考评分；同一战役跨章节保留记录。', 'penalty_launch_hint': '', 'penalty_plugin_install_success': '评分系统插件已安装。', 'penalty_plugin_install_vpk_success': '评分系统插件已安装。', 'penalty_plugin_install_folder_success': '评分系统插件已安装。'},
    'zh_CN': {'plugin_hud_title': 'Danyria 插件', 'plugin_hud_subtitle': '外置 HUD：速度表 + 敌人血量显示。', 'hud_plugin_status': 'Danyria 插件状态', 'hud_plugin_desc': 'Danyria 插件：写出速度、血量和敌人数据。', 'hud_launch_hint': '', 'hud_plugin_install_success': 'HUD 遥测插件已安装。', 'hud_plugin_install_vpk_success': 'HUD 遥测插件已安装。', 'hud_plugin_install_folder_success': 'HUD 遥测插件已安装。', 'plugin_penalty_title': '评分系统插件（测试项目）', 'plugin_penalty_subtitle': '测试项目：个人击杀、治疗、受伤、物资和输出统计 HUD。', 'penalty_plugin_desc': '评分系统测试插件：写出个人统计和评分数据。', 'penalty_mechanism_desc': '实时读取玩家自己的受伤、倒地/死亡、救援、治疗、击杀、伤害输出和物资使用，生成个人参考评分；同一战役跨章节保留记录。', 'penalty_launch_hint': '', 'penalty_plugin_install_success': '评分系统插件已安装。', 'penalty_plugin_install_vpk_success': '评分系统插件已安装。', 'penalty_plugin_install_folder_success': '评分系统插件已安装。'},
    'en': {'plugin_hud_title': 'Danyria plugin', 'plugin_hud_subtitle': 'External HUD: speedometer + enemy health display.', 'hud_plugin_status': 'Danyria plugin status', 'hud_plugin_desc': 'Danyria plugin: writes speed, health, and enemy data.', 'hud_launch_hint': '', 'hud_plugin_install_success': 'HUD telemetry plugin installed.', 'hud_plugin_install_vpk_success': 'HUD telemetry plugin installed.', 'hud_plugin_install_folder_success': 'HUD telemetry plugin installed.', 'plugin_penalty_title': 'Score System Plugin (Test)', 'plugin_penalty_subtitle': 'Test item: personal kills, healing, damage taken, supplies, and output statistics HUD.', 'penalty_plugin_desc': 'Score-system test plugin: writes personal statistics and score data.', 'penalty_mechanism_desc': 'Reads your own damage taken, incaps/deaths, revives, healing, kills, damage output, and supplies to produce a personal reference score that is kept across campaign chapters.', 'penalty_launch_hint': '', 'penalty_plugin_install_success': 'Score system plugin installed.', 'penalty_plugin_install_vpk_success': 'Score system plugin installed.', 'penalty_plugin_install_folder_success': 'Score system plugin installed.'},
    'ja': {'plugin_hud_title': 'Danyria plugin', 'plugin_hud_subtitle': 'External HUD: speedometer + enemy health display.', 'hud_plugin_status': 'Danyria plugin status', 'hud_plugin_desc': 'Danyria plugin: writes speed, health, and enemy data.', 'hud_launch_hint': '', 'hud_plugin_install_success': 'HUD telemetry plugin installed.', 'hud_plugin_install_vpk_success': 'HUD telemetry plugin installed.', 'hud_plugin_install_folder_success': 'HUD telemetry plugin installed.', 'plugin_penalty_title': 'Score System Plugin (Test)', 'plugin_penalty_subtitle': 'Test item: personal kills, healing, damage taken, supplies, and output statistics HUD.', 'penalty_plugin_desc': 'Score-system test plugin: writes personal statistics and score data.', 'penalty_mechanism_desc': 'Reads your own damage taken, incaps/deaths, revives, healing, kills, damage output, and supplies to produce a personal reference score that is kept across campaign chapters.', 'penalty_launch_hint': '', 'penalty_plugin_install_success': 'Score system plugin installed.', 'penalty_plugin_install_vpk_success': 'Score system plugin installed.', 'penalty_plugin_install_folder_success': 'Score system plugin installed.'},
    'ko': {'plugin_hud_title': 'Danyria plugin', 'plugin_hud_subtitle': 'External HUD: speedometer + enemy health display.', 'hud_plugin_status': 'Danyria plugin status', 'hud_plugin_desc': 'Danyria plugin: writes speed, health, and enemy data.', 'hud_launch_hint': '', 'hud_plugin_install_success': 'HUD telemetry plugin installed.', 'hud_plugin_install_vpk_success': 'HUD telemetry plugin installed.', 'hud_plugin_install_folder_success': 'HUD telemetry plugin installed.', 'plugin_penalty_title': 'Score System Plugin (Test)', 'plugin_penalty_subtitle': 'Test item: personal kills, healing, damage taken, supplies, and output statistics HUD.', 'penalty_plugin_desc': 'Score-system test plugin: writes personal statistics and score data.', 'penalty_mechanism_desc': 'Reads your own damage taken, incaps/deaths, revives, healing, kills, damage output, and supplies to produce a personal reference score that is kept across campaign chapters.', 'penalty_launch_hint': '', 'penalty_plugin_install_success': 'Score system plugin installed.', 'penalty_plugin_install_vpk_success': 'Score system plugin installed.', 'penalty_plugin_install_folder_success': 'Score system plugin installed.'},
    'ru': {'plugin_hud_title': 'Danyria plugin', 'plugin_hud_subtitle': 'External HUD: speedometer + enemy health display.', 'hud_plugin_status': 'Danyria plugin status', 'hud_plugin_desc': 'Danyria plugin: writes speed, health, and enemy data.', 'hud_launch_hint': '', 'hud_plugin_install_success': 'HUD telemetry plugin installed.', 'hud_plugin_install_vpk_success': 'HUD telemetry plugin installed.', 'hud_plugin_install_folder_success': 'HUD telemetry plugin installed.', 'plugin_penalty_title': 'Score System Plugin (Test)', 'plugin_penalty_subtitle': 'Test item: personal kills, healing, damage taken, supplies, and output statistics HUD.', 'penalty_plugin_desc': 'Score-system test plugin: writes personal statistics and score data.', 'penalty_mechanism_desc': 'Reads your own damage taken, incaps/deaths, revives, healing, kills, damage output, and supplies to produce a personal reference score that is kept across campaign chapters.', 'penalty_launch_hint': '', 'penalty_plugin_install_success': 'Score system plugin installed.', 'penalty_plugin_install_vpk_success': 'Score system plugin installed.', 'penalty_plugin_install_folder_success': 'Score system plugin installed.'},
    'de': {'plugin_hud_title': 'Danyria plugin', 'plugin_hud_subtitle': 'External HUD: speedometer + enemy health display.', 'hud_plugin_status': 'Danyria plugin status', 'hud_plugin_desc': 'Danyria plugin: writes speed, health, and enemy data.', 'hud_launch_hint': '', 'hud_plugin_install_success': 'HUD telemetry plugin installed.', 'hud_plugin_install_vpk_success': 'HUD telemetry plugin installed.', 'hud_plugin_install_folder_success': 'HUD telemetry plugin installed.', 'plugin_penalty_title': 'Score System Plugin (Test)', 'plugin_penalty_subtitle': 'Test item: personal kills, healing, damage taken, supplies, and output statistics HUD.', 'penalty_plugin_desc': 'Score-system test plugin: writes personal statistics and score data.', 'penalty_mechanism_desc': 'Reads your own damage taken, incaps/deaths, revives, healing, kills, damage output, and supplies to produce a personal reference score that is kept across campaign chapters.', 'penalty_launch_hint': '', 'penalty_plugin_install_success': 'Score system plugin installed.', 'penalty_plugin_install_vpk_success': 'Score system plugin installed.', 'penalty_plugin_install_folder_success': 'Score system plugin installed.'},
    'fr': {'plugin_hud_title': 'Danyria plugin', 'plugin_hud_subtitle': 'External HUD: speedometer + enemy health display.', 'hud_plugin_status': 'Danyria plugin status', 'hud_plugin_desc': 'Danyria plugin: writes speed, health, and enemy data.', 'hud_launch_hint': '', 'hud_plugin_install_success': 'HUD telemetry plugin installed.', 'hud_plugin_install_vpk_success': 'HUD telemetry plugin installed.', 'hud_plugin_install_folder_success': 'HUD telemetry plugin installed.', 'plugin_penalty_title': 'Score System Plugin (Test)', 'plugin_penalty_subtitle': 'Test item: personal kills, healing, damage taken, supplies, and output statistics HUD.', 'penalty_plugin_desc': 'Score-system test plugin: writes personal statistics and score data.', 'penalty_mechanism_desc': 'Reads your own damage taken, incaps/deaths, revives, healing, kills, damage output, and supplies to produce a personal reference score that is kept across campaign chapters.', 'penalty_launch_hint': '', 'penalty_plugin_install_success': 'Score system plugin installed.', 'penalty_plugin_install_vpk_success': 'Score system plugin installed.', 'penalty_plugin_install_folder_success': 'Score system plugin installed.'},
    'es': {'plugin_hud_title': 'Danyria plugin', 'plugin_hud_subtitle': 'External HUD: speedometer + enemy health display.', 'hud_plugin_status': 'Danyria plugin status', 'hud_plugin_desc': 'Danyria plugin: writes speed, health, and enemy data.', 'hud_launch_hint': '', 'hud_plugin_install_success': 'HUD telemetry plugin installed.', 'hud_plugin_install_vpk_success': 'HUD telemetry plugin installed.', 'hud_plugin_install_folder_success': 'HUD telemetry plugin installed.', 'plugin_penalty_title': 'Score System Plugin (Test)', 'plugin_penalty_subtitle': 'Test item: personal kills, healing, damage taken, supplies, and output statistics HUD.', 'penalty_plugin_desc': 'Score-system test plugin: writes personal statistics and score data.', 'penalty_mechanism_desc': 'Reads your own damage taken, incaps/deaths, revives, healing, kills, damage output, and supplies to produce a personal reference score that is kept across campaign chapters.', 'penalty_launch_hint': '', 'penalty_plugin_install_success': 'Score system plugin installed.', 'penalty_plugin_install_vpk_success': 'Score system plugin installed.', 'penalty_plugin_install_folder_success': 'Score system plugin installed.'}}
I18N = _merge_i18n_pack(I18N, I18N_PLUGIN_TEXT_PATCH)

I18N_SCORE_REFERENCE = {
    "zh": {
        "score_reference_title": "计分参考（100 分制）",
        "score_reference_text": "用于说明评分 HUD 的数据来源和统计范围：优先读取 Danyria 绑定的玩家个人数据，并在同一战役跨章节保留。统计项包括击杀、治疗、受伤、倒地、挂边、死亡、物资使用与输出伤害；队伍状态只显示，不接管队友数据。"
    },
    "en": {
        "score_reference_title": "Score reference (100-point scale)",
        "score_reference_text": "Explains the data source and scope of the score HUD. It prefers the bound player data read by Danyria and keeps it across campaign chapters. Tracked items include kills, healing, damage taken, incaps, ledge grabs, deaths, supplies, and damage output; team status is display-only."
    },
    "ja": {
        "score_reference_title": "スコア参考（100点制）",
        "score_reference_text": "用于说明评分 HUD 的数据来源和统计范围：优先读取 Danyria 绑定的玩家个人数据，并在同一战役跨章节保留。统计项包括击杀、治疗、受伤、倒地、挂边、死亡、物资使用与输出伤害；队伍状态只显示，不接管队友数据。"
    },
    "ko": {
        "score_reference_title": "점수 참고（100점 기준）",
        "score_reference_text": "Explains the data source and scope of the score HUD. It prefers the bound player data read by Danyria and keeps it across campaign chapters. Tracked items include kills, healing, damage taken, incaps, ledge grabs, deaths, supplies, and damage output; team status is display-only."
    },
    "ru": {
        "score_reference_title": "Справка по счёту (100-балльная шкала)",
        "score_reference_text": "Explains the data source and scope of the score HUD. It prefers the bound player data read by Danyria and keeps it across campaign chapters. Tracked items include kills, healing, damage taken, incaps, ledge grabs, deaths, supplies, and damage output; team status is display-only."
    },
    "de": {
        "score_reference_title": "Wertungsreferenz (100 Punkte)",
        "score_reference_text": "Explains the data source and scope of the score HUD. It prefers the bound player data read by Danyria and keeps it across campaign chapters. Tracked items include kills, healing, damage taken, incaps, ledge grabs, deaths, supplies, and damage output; team status is display-only."
    },
    "fr": {
        "score_reference_title": "Référence score (sur 100)",
        "score_reference_text": "Explains the data source and scope of the score HUD. It prefers the bound player data read by Danyria and keeps it across campaign chapters. Tracked items include kills, healing, damage taken, incaps, ledge grabs, deaths, supplies, and damage output; team status is display-only."
    },
    "es": {
        "score_reference_title": "Referencia de puntuación (100 puntos)",
        "score_reference_text": "Explains the data source and scope of the score HUD. It prefers the bound player data read by Danyria and keeps it across campaign chapters. Tracked items include kills, healing, damage taken, incaps, ledge grabs, deaths, supplies, and damage output; team status is display-only."
    }
}
I18N = _merge_i18n_pack(I18N, I18N_SCORE_REFERENCE)

I18N_SCORE_CUSTOM = {
    "zh": {
        "score_custom_title": "自定义评分",
        "score_custom_hint": "可填写正数或负数；正数加分，负数扣分。伤害奖励分和伤害奖励触发间隔是联动项：每造成指定间隔的伤害，就按伤害奖励分结算一次。",
        "score_rule_common": "普感击杀",
        "score_rule_special": "特感击杀",
        "score_rule_witch": "Witch 击杀",
        "score_rule_tank": "Tank 击杀",
        "score_rule_damage_done_score": "伤害奖励分（联动）",
        "score_rule_damage_done_step": "伤害奖励触发间隔",
        "score_rule_damage_taken_per10": "每10点受伤",
                "score_rule_incap": "倒地",
        "score_rule_death": "死亡",
        "score_rule_ledge": "挂边",
        "score_rule_revive": "救援队友",
                "score_rule_heal": "医疗包",
        "score_rule_pills": "药丸",
        "score_rule_adrenaline": "肾上腺素",
        "score_rule_supply_small": "小物资",
                "score_rule_supply_weapon": "武器/弹药"
    },
    "en": {
        "score_custom_title": "Custom score values",
        "score_custom_hint": "Use positive values to add score and negative values to subtract score. Damage bonus and damage step are linked: every configured damage step awards the damage bonus once.",
        "score_rule_common": "Common kill",
        "score_rule_special": "Special kill",
        "score_rule_witch": "Witch kill",
        "score_rule_tank": "Tank kill",
        "score_rule_damage_done_score": "Damage bonus per step",
        "score_rule_damage_done_step": "Damage bonus step",
        "score_rule_damage_taken_per10": "Per 10 damage taken",
                "score_rule_incap": "Incap",
        "score_rule_death": "Death",
        "score_rule_ledge": "Ledge grab",
        "score_rule_revive": "Revive teammate",
                "score_rule_heal": "First aid",
        "score_rule_pills": "Pills",
        "score_rule_adrenaline": "Adrenaline",
        "score_rule_supply_small": "Small supply",
                "score_rule_supply_weapon": "Weapon/ammo"
    }
}
for _lang in list(I18N.keys()):
    if _lang not in I18N_SCORE_CUSTOM:
        I18N_SCORE_CUSTOM[_lang] = dict(I18N_SCORE_CUSTOM["en"])
I18N = _merge_i18n_pack(I18N, I18N_SCORE_CUSTOM)

I18N_SCORE_PARAM_BUTTONS = {
    "zh": {
        "score_save_params": "保存参数",
        "score_reset_params": "恢复默认参数",
        "score_params_saved": "参数已保存。重启外置 HUD 后生效。",
        "score_params_reset": "评分参数已恢复默认。重启外置 HUD 后生效。"
    },
    "en": {
        "score_save_params": "Save Parameters",
        "score_reset_params": "Restore Default Parameters",
        "score_params_saved": "Parameters saved. Restart the external HUD to apply them.",
        "score_params_reset": "Score parameters restored. Restart the external HUD to apply them."
    }
}
for _lang in list(I18N.keys()):
    if _lang not in I18N_SCORE_PARAM_BUTTONS:
        I18N_SCORE_PARAM_BUTTONS[_lang] = dict(I18N_SCORE_PARAM_BUTTONS["en"])
I18N = _merge_i18n_pack(I18N, I18N_SCORE_PARAM_BUTTONS)


I18N_WORKSHOP = {
    "zh": {
        "launch_l4d2": "启动求生之路2",
        "sync_workshop": "同步创意工坊",
        "unsubscribe_workshop_selected": "取消订阅选中项",
        "restore_workshop_history": "管理历史记录",
        "workshop_sync_done": "已同步创意工坊：列表中包含 {n} 个来自 Workshop 的项目。",
        "workshop_no_id": "选中项没有 Workshop ID。",
        "workshop_manage_hint": "订阅操作会优先在 Danyria 内通过 Steam 联动执行；取消订阅会写入历史，之后可在管理历史记录里恢复。",
        "workshop_unsubscribe_done": "已向 Steam 提交取消订阅：{n} 项。",
        "workshop_subscribe_done": "已向 Steam 提交订阅：{n} 项。",
        "steam_direct_failed": "Steam 联动没有完成：{reason}",
        "steam_missing_api": "未找到 Steam API 组件。请先设置求生之路2路径或启动 Steam 后再检查环境。",
        "steam_init_failed": "Steam 初始化失败。请确认 Steam 已启动并登录。",
        "steam_ugc_failed": "Steam UGC 接口不可用。",
        "workshop_history_title": "管理历史记录",
        "workshop_history_empty": "没有取消订阅历史。",
        "workshop_history_open_selected": "打开选中项",
        "workshop_history_forget_selected": "删除选中项记录",
        "workshop_history_close": "关闭",
        "workshop_history_saved": "已记录到取消订阅历史：{n} 项。",
        "workshop_open_subscriptions": "打开订阅列表",
        "workshop_open_page_selected": "打开选中项页面",
        "workshop_history_subscribe_selected": "恢复订阅选中项",
        "workshop_history_clear": "清空历史",
        "workshop_history_restore_tip": "历史记录会保存取消订阅时的 Workshop ID、名称、路径和时间；选中项记录后可以打开页面、恢复订阅或删除记录。",
        "mod_group_selected": "选中项操作",
        "mod_group_local": "本地文件",
        "mod_group_workshop": "创意工坊",
        "mod_group_steam": "Steam 联动",
        "steam_connect": "连接 Steam",
        "steam_direct_unsubscribe": "Steam 取消订阅",
        "steam_status_connected": "Steam：已连接",
        "steam_status_not_running": "Steam：未连接",
        "steam_status_bridge_missing": "Steam 联动组件未就绪",
        "steam_bridge_failed": "Steam 联动未完成。",
        "runtime_status_steam_bridge_ok": "Steam 联动组件：已自动准备",
        "runtime_status_steam_bridge_missing": "Steam 联动组件：等待 Steam API",
        "runtime_status_steam_bridge_scaffold": "Steam 联动组件：已自动准备",
        "status_Subscribed": "已订阅",
        "status_Missing": "已订阅 / 本地缺失",
        "workshop_badge_subscribed": "[已订阅]",
        "workshop_badge_missing": "[已订阅 / 本地缺失]",
        "workshop_badge_local": "[Workshop 本地文件]",
        "workshop_badge_disabled": "[Workshop 已禁用]",
        "workshop_badge_unknown": "[Workshop]",
        "kind_Workshop": "Workshop 项目",
        "detail_workshop_manage": "管理提示",
    },
    "en": {
        "launch_l4d2": "Launch Left 4 Dead 2",
        "sync_workshop": "Sync Workshop",
        "unsubscribe_workshop_selected": "Unsubscribe Selected",
        "restore_workshop_history": "Manage History",
        "workshop_sync_done": "Workshop synced: {n} Workshop item(s) are now listed.",
        "workshop_no_id": "The selected item has no Workshop ID.",
        "workshop_manage_hint": "Subscription actions run through Danyria Steam Link first. Unsubscribe actions are recorded and can be restored later.",
        "workshop_unsubscribe_done": "Unsubscribe request sent to Steam: {n} item(s).",
        "workshop_subscribe_done": "Subscribe request sent to Steam: {n} item(s).",
        "steam_direct_failed": "Steam Link did not finish: {reason}",
        "steam_missing_api": "Steam API component was not found. Set the Left 4 Dead 2 path or start Steam, then run the environment check again.",
        "steam_init_failed": "Steam initialization failed. Make sure Steam is running and signed in.",
        "steam_ugc_failed": "Steam UGC interface is unavailable.",
        "workshop_history_title": "Unsubscribe History",
        "workshop_history_empty": "No unsubscribe history yet.",
        "workshop_history_open_selected": "Restore Selected",
        "workshop_history_forget_selected": "Forget Selected",
        "workshop_history_close": "Close",
        "workshop_history_saved": "Saved to unsubscribe history: {n} item(s).",
        "workshop_open_subscriptions": "Open Subscriptions",
        "workshop_open_page_selected": "Open Selected Item Page",
        "workshop_history_subscribe_selected": "Resubscribe Selected Item",
        "workshop_history_clear": "Clear History",
        "workshop_history_restore_tip": "The history keeps Workshop ID, title, path, and time. Select items to open pages, resubscribe, or delete records.",
        "mod_group_selected": "Selected Item",
        "mod_group_local": "Local Files",
        "mod_group_workshop": "Workshop",
        "mod_group_steam": "Steam Link",
        "steam_connect": "Connect Steam",
        "steam_direct_unsubscribe": "Steam Unsubscribe",
        "steam_status_connected": "Steam: connected",
        "steam_status_not_running": "Steam: disconnected",
        "steam_status_bridge_missing": "Steam Link component is not ready.",
        "steam_bridge_failed": "Steam Link did not finish.",
        "runtime_status_steam_bridge_ok": "Steam Link component: ready",
        "runtime_status_steam_bridge_missing": "Steam Link component: waiting for Steam API",
        "runtime_status_steam_bridge_scaffold": "Steam Link component: ready",
        "status_Subscribed": "Subscribed",
        "status_Missing": "Subscribed / Missing Local File",
        "workshop_badge_subscribed": "[Subscribed]",
        "workshop_badge_missing": "[Subscribed / Missing Local File]",
        "workshop_badge_local": "[Local Workshop File]",
        "workshop_badge_disabled": "[Disabled Workshop]",
        "workshop_badge_unknown": "[Workshop]",
        "kind_Workshop": "Workshop Item",
        "detail_workshop_manage": "Manage Hint",
    }
}
I18N = _merge_i18n_pack(I18N, I18N_WORKSHOP)


# ---------------------------------------------------------------------------
# 扫描结果和 VPK 索引使用的数据模型。
# Data models used for scan results and VPK indexes.
# ---------------------------------------------------------------------------
@dataclass
class ModRecord:
    title: str
    category: str
    kind: str
    source: str
    status: str
    path: str
    size_mb: float = 0.0
    author: str = ""
    description: str = ""
    modified: str = ""
    tags: list[str] = field(default_factory=list)
    evidence: list[str] = field(default_factory=list)
    valid: bool = True
    workshop_id: str = ""


@dataclass
class WeaponValueEntry:
    key: str
    value: str
    original: str
    line_no: int
    prefix: str
    suffix: str
    newline: str


@dataclass
class WeaponScriptRecord:
    title: str
    kind: str
    path: str
    rel_path: str = ""
    origin: str = ""
    workspace: bool = False
    entries: list[WeaponValueEntry] = field(default_factory=list)
    lines: list[str] = field(default_factory=list)
    metrics: dict = field(default_factory=dict)
    rank: int = 0

def base_dir() -> Path:
    # 中文：运行目录用于存放用户配置和外置文件；打包后指向 exe 所在目录。
    # English: Runtime directory stores user config and external files; in frozen builds it points to the exe folder.
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent

def resource_dir() -> Path:
    # 中文：资源目录用于读取 PyInstaller/Nuitka 打包进程序的 assets/payload。
    # English: Resource directory reads assets/payload bundled by PyInstaller/Nuitka.
    try:
        return Path(getattr(sys, "_MEIPASS", "")).resolve() if getattr(sys, "_MEIPASS", None) else Path(__file__).resolve().parent
    except Exception:
        return Path(__file__).resolve().parent

def first_existing_dir(*relative_parts: str) -> Path:
    rel = Path(*relative_parts)
    for root in (base_dir(), resource_dir(), Path(__file__).resolve().parent):
        candidate = root / rel
        if candidate.exists():
            return candidate
    return base_dir() / rel

def app_data_dir() -> Path:
    # 中文：打包版优先使用 AppData 保存运行时配置，避免写入一次性解包目录。
    # English: Frozen builds prefer AppData for runtime config instead of the temporary extraction folder.
    if os.name == "nt":
        root = os.environ.get("APPDATA") or str(base_dir())
        return Path(root) / APP_NAME
    return Path.home() / ".danyria"

def cfg_path() -> Path:
    if getattr(sys, "frozen", False):
        return app_data_dir() / CONFIG_NAME
    return base_dir() / CONFIG_NAME

def read_text_safe(path: Path) -> str:
    for enc in ("utf-8-sig", "utf-8", "gbk", "latin-1"):
        try:
            return path.read_text(encoding=enc, errors="replace")
        except Exception:
            pass
    return ""

def parse_keyvalues_flat(text: str) -> dict[str, str]:
    text = re.sub(r"//.*?$", "", text, flags=re.MULTILINE)
    out = {}
    for m in re.finditer(r'"?([A-Za-z0-9_]+)"?\s+"([^"]*)"', text):
        out[m.group(1).lower()] = m.group(2).strip()
    for m in re.finditer(r'"?([A-Za-z0-9_]+)"?\s+([A-Za-z0-9_.:/\\\-]+)', text):
        k = m.group(1).lower()
        if k not in out and k not in ("addoninfo",):
            out[k] = m.group(2).strip().strip('"')
    return out



def _extract_vdf_section(text: str, section_name: str) -> str:
    m = re.search(r'"' + re.escape(section_name) + r'"\s*\{', text, flags=re.IGNORECASE)
    if not m:
        return ""
    start = text.find("{", m.start())
    if start < 0:
        return ""
    depth = 0
    in_quote = False
    esc = False
    for i in range(start, len(text)):
        ch = text[i]
        if in_quote:
            if esc:
                esc = False
            elif ch == "\\":
                esc = True
            elif ch == '"':
                in_quote = False
            continue
        if ch == '"':
            in_quote = True
        elif ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                return text[start + 1:i]
    return ""


def _iter_vdf_numeric_blocks(section_body: str):
    pos = 0
    while True:
        m = re.search(r'"(\d+)"\s*\{', section_body[pos:])
        if not m:
            break
        key = m.group(1)
        start = pos + m.end() - 1
        depth = 0
        in_quote = False
        esc = False
        end = -1
        for i in range(start, len(section_body)):
            ch = section_body[i]
            if in_quote:
                if esc:
                    esc = False
                elif ch == "\\":
                    esc = True
                elif ch == '"':
                    in_quote = False
                continue
            if ch == '"':
                in_quote = True
            elif ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0:
                    end = i
                    break
        if end < 0:
            break
        yield key, section_body[start + 1:end]
        pos = end + 1


def workshop_acf_path_for_l4d2(l4d2: Path) -> Optional[Path]:
    candidates = []
    try:
        candidates.append(l4d2.parent.parent.parent / "workshop" / f"appworkshop_{L4D2_APP_ID}.acf")
    except Exception:
        pass
    for lib in find_steam_libraries():
        candidates.append(lib / "steamapps" / "workshop" / f"appworkshop_{L4D2_APP_ID}.acf")
    seen = set()
    for p in candidates:
        k = str(p).lower()
        if k in seen:
            continue
        seen.add(k)
        if p.exists():
            return p
    return None


def read_l4d2_workshop_manifest(l4d2: Path) -> dict[str, dict[str, str]]:
    acf = workshop_acf_path_for_l4d2(l4d2)
    if not acf:
        return {}
    text = read_text_safe(acf)
    items: dict[str, dict[str, str]] = {}
    for section_name in ("WorkshopItemsInstalled", "WorkshopItemDetails"):
        body = _extract_vdf_section(text, section_name)
        for wid, block in _iter_vdf_numeric_blocks(body):
            data = parse_keyvalues_flat(block)
            cur = items.setdefault(wid, {})
            cur.update(data)
            cur["id"] = wid
            cur["acf_path"] = str(acf)
    return items


def workshop_content_path_for_id(l4d2: Path, wid: str) -> Optional[Path]:
    candidates = []
    try:
        candidates.append(l4d2.parent.parent.parent / "workshop" / "content" / L4D2_APP_ID / wid)
    except Exception:
        pass
    for lib in find_steam_libraries():
        candidates.append(lib / "steamapps" / "workshop" / "content" / L4D2_APP_ID / wid)
    seen = set()
    for p in candidates:
        k = str(p).lower()
        if k in seen:
            continue
        seen.add(k)
        if p.exists():
            return p
    return None

def modified_str(path: Path) -> str:
    try:
        return time.strftime("%Y-%m-%d %H:%M", time.localtime(path.stat().st_mtime))
    except Exception:
        return ""

def file_size_mb(path: Path) -> float:
    try:
        return round(path.stat().st_size / 1024 / 1024, 2)
    except Exception:
        return 0.0

def folder_size_mb(path: Path, limit_files=8000) -> float:
    total = 0
    n = 0
    try:
        for p in path.rglob("*"):
            if p.is_file():
                n += 1
                if n > limit_files:
                    break
                try:
                    total += p.stat().st_size
                except Exception:
                    pass
    except Exception:
        pass
    return round(total / 1024 / 1024, 2)

def is_vpk_magic(path: Path) -> bool:
    try:
        with path.open("rb") as f:
            b = f.read(4)
        return len(b) == 4 and struct.unpack("<I", b)[0] == VPK_MAGIC
    except Exception:
        return False

@dataclass
class VpkEntry:
    rel: str
    preload: bytes
    archive_index: int
    offset: int
    length: int

# ---------------------------------------------------------------------------
# VPK 读取与 MOD 内容分析工具。
# VPK reading and mod-content analysis helpers.
# ---------------------------------------------------------------------------
def parse_vpk(path: Path, limit=50000) -> tuple[list[str], dict[str, VpkEntry], bool, str, int]:
    names: list[str] = []
    entries: dict[str, VpkEntry] = {}
    try:
        with path.open("rb") as f:
            header = f.read(12)
            if len(header) < 12:
                return names, entries, False, "too small", 0
            sig, version, tree_size = struct.unpack("<III", header)
            if sig != VPK_MAGIC:
                return names, entries, False, "bad magic", 0
            if version not in (1, 2):
                return names, entries, True, f"unknown VPK version {version}", 0

            header_size = 28 if version == 2 else 12
            f.seek(header_size)
            tree_data = f.read(tree_size)
            data_base = header_size + tree_size
            tree = io.BytesIO(tree_data)

            def cstr() -> str:
                buf = bytearray()
                while True:
                    b = tree.read(1)
                    if not b:
                        return ""
                    if b == b"\x00":
                        return buf.decode("utf-8", errors="replace")
                    buf.extend(b)

            while True:
                ext = cstr()
                if ext == "":
                    break
                while True:
                    folder = cstr()
                    if folder == "":
                        break
                    while True:
                        name = cstr()
                        if name == "":
                            break
                        raw = tree.read(18)
                        if len(raw) < 18:
                            return names, entries, True, "truncated tree", data_base
                        crc, preload_len, archive_index, offset, length, terminator = struct.unpack("<IHHIIH", raw)
                        preload = tree.read(preload_len) if preload_len else b""
                        folder_clean = "" if folder in (" ", "") else folder.strip("/")
                        rel = f"{folder_clean}/{name}.{ext}" if folder_clean else f"{name}.{ext}"
                        rel = rel.lower().replace("\\", "/")
                        names.append(rel)
                        entries[rel] = VpkEntry(rel, preload, archive_index, offset, length)
                        if len(names) >= limit:
                            return names, entries, True, f"listed first {limit} files", data_base
            return names, entries, True, f"listed {len(names)} files", data_base
    except Exception as exc:
        return names, entries, False, f"read failed: {exc}", 0

def vpk_archive_path(dir_vpk: Path, archive_index: int) -> Path:
    stem = dir_vpk.stem
    suffix = dir_vpk.suffix
    if stem.lower().endswith("_dir"):
        base = stem[:-4]
    else:
        base = stem
    return dir_vpk.with_name(f"{base}_{archive_index:03d}{suffix}")


def read_vpk_file(path: Path, entries: dict[str, VpkEntry], data_base: int, relname: str, max_bytes=16*1024*1024) -> bytes:
    ent = entries.get(relname.lower())
    if not ent:
        for k, v in entries.items():
            if k.endswith("/" + relname.lower()) or k == relname.lower():
                ent = v
                break
    if not ent:
        return b""
    data = bytearray(ent.preload or b"")
    if ent.length > 0:
        try:
            if ent.archive_index == DIR_INDEX:
                data_path = path
                seek_to = data_base + ent.offset
            else:
                data_path = vpk_archive_path(path, ent.archive_index)
                seek_to = ent.offset
            with data_path.open("rb") as f:
                f.seek(seek_to)
                data.extend(f.read(min(ent.length, max_bytes)))
        except Exception:
            pass
    return bytes(data[:max_bytes])


def is_weapon_script_rel(rel: str) -> bool:
    r = _weapon_rel(rel)
    name = Path(r).name.lower()
    if r.startswith("scripts/melee/"):
        return name in OFFICIAL_MELEE_SCRIPT_NAMES
    if r.startswith("scripts/"):
        return name in OFFICIAL_GUN_SCRIPT_NAMES or name in OFFICIAL_SPECIAL_MELEE_SCRIPT_NAMES
    return False


def kind_from_weapon_rel(rel: str) -> str:
    r = _weapon_rel(rel)
    name = Path(r).name.lower()
    if r.startswith("scripts/melee/") or name in OFFICIAL_SPECIAL_MELEE_SCRIPT_NAMES:
        return "melee"
    return "gun"


def ensure_weapon_addoninfo(project_dir: Path):
    addoninfo = project_dir / "addoninfo.txt"
    if addoninfo.exists():
        return
    addoninfo.write_text(
        '"AddonInfo"\n{\n'
        '    "addonTitle" "Danyria Weapon Values"\n'
        '    "addonVersion" "1.0.0"\n'
        '    "addonAuthor" "B站 千早ですわ"\n'
        '    "addonDescription" "Weapon script overrides generated by Danyria."\n'
        '    "addonContent_Script" "1"\n'
        '}\n',
        encoding="utf-8"
    )

def _write_cstr(buf: io.BytesIO, text: str):
    buf.write(text.encode("utf-8", errors="replace"))
    buf.write(b"\x00")


def write_simple_vpk(source_dir: Path, dest_vpk: Path):
    source_dir = source_dir.resolve()
    files = []
    for p in sorted(source_dir.rglob("*")):
        if p.is_file():
            rel = p.relative_to(source_dir).as_posix().lower()
            files.append((rel, p))
    if not files:
        raise ValueError("empty VPK source folder")

    groups: dict[str, dict[str, list[tuple[str, str, Path]]]] = {}
    for rel, p in files:
        rel_path = Path(rel)
        ext = rel_path.suffix[1:] or " "
        folder = rel_path.parent.as_posix()
        if folder == ".":
            folder = " "
        name = rel_path.stem
        groups.setdefault(ext, {}).setdefault(folder, []).append((name, rel, p))

    tree = io.BytesIO()
    data_chunks: list[bytes] = []
    data_offset = 0
    for ext in sorted(groups):
        _write_cstr(tree, ext)
        for folder in sorted(groups[ext]):
            _write_cstr(tree, folder)
            for name, rel, p in sorted(groups[ext][folder], key=lambda x: x[1]):
                payload = p.read_bytes()
                crc = zlib.crc32(payload) & 0xFFFFFFFF
                _write_cstr(tree, name)
                tree.write(struct.pack("<IHHIIH", crc, 0, DIR_INDEX, data_offset, len(payload), 0xFFFF))
                data_chunks.append(payload)
                data_offset += len(payload)
            _write_cstr(tree, "")
        _write_cstr(tree, "")
    _write_cstr(tree, "")

    tree_data = tree.getvalue()
    dest_vpk.parent.mkdir(parents=True, exist_ok=True)
    with dest_vpk.open("wb") as f:
        f.write(struct.pack("<III", VPK_MAGIC, 1, len(tree_data)))
        f.write(tree_data)
        for chunk in data_chunks:
            f.write(chunk)

def source_for(path: Path, l4d2: Path) -> str:
    s = str(path).lower().replace("/", "\\")
    workshop = str((l4d2 / "addons" / "workshop")).lower().replace("/", "\\")
    addons = str((l4d2 / "addons")).lower().replace("/", "\\")
    if s.startswith(workshop + "\\"):
        return "Workshop"
    if s.startswith(addons + "\\"):
        return "Local"
    return "Unknown"

def classify_mod(title: str, desc: str, addoninfo: dict[str, str], rels: list[str]) -> tuple[str, list[str], list[str]]:
    rels = [r.lower().replace("\\", "/").lstrip("/") for r in rels]
    hay = f" {title} {desc} ".lower()

    evidence: list[str] = []
    tags: list[str] = []

    def add(text: str):
        evidence.append(text)

    def mark(tag: str):
        tags.append(tag)

    def count_where(pred):
        return sum(1 for r in rels if pred(r))

    def has_any_token(r: str, tokens: list[str]) -> bool:
        return any(tok in r for tok in tokens)

    def is_sound_path(r: str) -> bool:
        return r.startswith("sound/") or r.startswith("music/")

    def is_sound_script(r: str) -> bool:
        return (
            r.startswith("scripts/game_sounds") or
            r.startswith("scripts/level_sounds") or
            r.startswith("scripts/music")
        )

    def is_model_material_or_script(r: str) -> bool:
        return (
            r.startswith("models/") or
            r.startswith("materials/") or
            (r.startswith("scripts/") and not is_sound_script(r)) or
            r.startswith("particles/")
        )

    medical_tokens = [
        "first_aid", "firstaid", "medkit", "med_kit", "pain_pills", "pills",
        "adrenaline", "defibrillator", "defib", "healthkit",
    ]
    throwable_tokens = [
        "molotov", "pipe_bomb", "pipebomb", "vomitjar", "vomit_jar",
        "boomer_bile", "bile_flask",
    ]
    carryable_tokens = [
        "gascan", "gas_can", "propane", "propanetank", "propane_tank",
        "oxygen_tank", "oxygentank", "fireworkcrate", "fireworks",
        "cola_bottles", "cola", "gnome", "scavenge", "carryable",
    ]
    special_item_tokens = medical_tokens + throwable_tokens + carryable_tokens
    weapon_tokens = [
        "rifle", "m16", "ak47", "ak-47", "scar", "sg552", "smg", "uzi", "mp5",
        "shotgun", "pumpshotgun", "autoshotgun", "chrome_shotgun", "spas",
        "pistol", "magnum", "deagle", "hunting_rifle", "sniper", "awp", "scout",
        "grenade_launcher", "m60", "chainsaw", "katana", "machete", "knife",
        "crowbar", "fireaxe", "axe", "baseball_bat", "cricket_bat", "frying_pan",
        "electric_guitar", "golfclub", "tonfa", "pitchfork", "shovel", "melee",
    ]

    mission_count = count_where(lambda r: r.startswith("missions/"))
    bsp_count = count_where(lambda r: r.startswith("maps/") and r.endswith(".bsp"))

    sound_file_count = count_where(lambda r: is_sound_path(r))
    sound_script_count = count_where(lambda r: is_sound_script(r))
    sound_total = sound_file_count + sound_script_count

    medical_visual_count = count_where(lambda r: has_any_token(r, medical_tokens) and is_model_material_or_script(r) and not is_sound_path(r))
    throwable_visual_count = count_where(lambda r: has_any_token(r, throwable_tokens) and is_model_material_or_script(r) and not is_sound_path(r))
    carryable_visual_count = count_where(lambda r: has_any_token(r, carryable_tokens) and is_model_material_or_script(r) and not is_sound_path(r))

    def is_special_item(r: str) -> bool:
        return has_any_token(r, special_item_tokens)

    def has_weapon_token(r: str) -> bool:
        return has_any_token(r, weapon_tokens)

    weapon_model_count = count_where(lambda r:
        not is_special_item(r) and (
            r.startswith("models/v_models/") or r.startswith("models/w_models/") or
            r.startswith("models/weapons/") or r.startswith("models/infected/weapons/") or
            (r.startswith("models/") and has_weapon_token(r) and not r.startswith("models/survivors/"))
        )
    )
    weapon_material_count = count_where(lambda r:
        not is_special_item(r) and (
            r.startswith("materials/models/weapons/") or r.startswith("materials/models/v_models/") or
            r.startswith("materials/models/w_models/") or r.startswith("materials/v_models/") or
            r.startswith("materials/w_models/") or
            (r.startswith("materials/models/") and has_weapon_token(r) and "/survivors/" not in r and "/infected/" not in r)
        )
    )
    weapon_item_script_count = count_where(lambda r:
        not is_special_item(r) and ((r.startswith("scripts/weapon") or r.startswith("scripts/melee")) and not is_sound_script(r))
    )
    weapon_particle_count = count_where(lambda r: not is_special_item(r) and r.startswith("particles/") and has_weapon_token(r))
    weapon_decisive_total = weapon_model_count + weapon_material_count + weapon_item_script_count + weapon_particle_count

    survivor_model_count = count_where(lambda r:
        r.startswith("models/survivors/") or r.startswith("materials/models/survivors/") or
        (r.startswith("materials/models/") and "survivor_" in r) or
        (r.startswith("models/") and "survivor_" in r)
    )
    infected_model_count = count_where(lambda r: r.startswith("models/infected/") or r.startswith("materials/models/infected/"))
    ui_count = count_where(lambda r:
        r.startswith("resource/ui/") or r.startswith("materials/vgui/") or
        r in ("scripts/hudlayout.res", "resource/clientscheme.res") or
        "/hud" in r or "hud_" in r or "crosshair" in r
    )
    vscript_count = count_where(lambda r:
        r.startswith("scripts/vscripts/") or r.startswith("modes/") or
        (r.endswith(".nut") and not is_sound_script(r))
    )
    effect_count = count_where(lambda r:
        r.startswith("particles/") or r.startswith("materials/effects/") or
        r.startswith("materials/sprites/") or r.startswith("scripts/particles")
    )
    prop_model_count = count_where(lambda r:
        r.startswith("models/props") or r.startswith("materials/models/props") or
        r.startswith("models/vehicles/") or r.startswith("materials/models/vehicles/")
    )
    texture_only_count = count_where(lambda r:
        r.startswith("materials/") and
        not r.startswith("materials/models/weapons/") and
        not r.startswith("materials/models/v_models/") and
        not r.startswith("materials/models/w_models/") and
        not r.startswith("materials/models/survivors/") and
        not r.startswith("materials/models/infected/") and
        not r.startswith("materials/models/props") and
        not r.startswith("materials/vgui/") and
        not r.startswith("materials/effects/") and
        not r.startswith("materials/sprites/")
    )

    decisive_non_sound_total = (
        medical_visual_count + throwable_visual_count + carryable_visual_count + weapon_decisive_total +
        survivor_model_count + infected_model_count + ui_count + vscript_count + prop_model_count +
        effect_count + texture_only_count + mission_count + bsp_count
    )

    evidence_pairs = [
        ("Mission files", mission_count, "mission"),
        ("Map files: maps/*.bsp", bsp_count, "map"),
        ("Sound files", sound_file_count, "sound"),
        ("Sound scripts: scripts/game_sounds*, level_sounds*, music*", sound_script_count, "sound_script"),
        ("Medical item visual/script signature", medical_visual_count, "medical"),
        ("Throwable visual/script signature", throwable_visual_count, "throwable"),
        ("Carryable / prop item visual signature", carryable_visual_count, "carryable"),
        ("Weapon model replacement signature", weapon_model_count, "weapon_model"),
        ("Weapon material replacement signature", weapon_material_count, "weapon_material"),
        ("Weapon item/melee script signature", weapon_item_script_count, "weapon_script"),
        ("Weapon particle signature", weapon_particle_count, "weapon_particle"),
        ("Survivor model/skin signature", survivor_model_count, "survivor"),
        ("Infected model/skin signature", infected_model_count, "infected"),
        ("HUD/UI signature", ui_count, "ui"),
        ("VScript/Mutation signature", vscript_count, "script"),
        ("Effects/particles signature", effect_count, "effects"),
        ("Props/world model signature", prop_model_count, "props"),
        ("Texture/material catch-all signature", texture_only_count, "texture"),
    ]
    for label, count, tag in evidence_pairs:
        if count:
            add(f"{label} = {count}")
            mark(tag)

    flag_categories: list[str] = []
    flag_map = {
        "addoncontent_script": "Mutation / Script",
        "addoncontent_map": "Map",
        "addoncontent_campaign": "Campaign",
        "addoncontent_survivor": "Character / Skin",
        "addoncontent_skin": "Character / Skin",
        "addoncontent_weapon": "Weapon",
        "addoncontent_weaponmodel": "Weapon",
        "addoncontent_sound": "Sound / Music",
        "addoncontent_music": "Sound / Music",
        "addoncontent_bossinfected": "Infected",
        "addoncontent_commoninfected": "Infected",
    }
    for key, cat in flag_map.items():
        val = addoninfo.get(key, "").strip().lower()
        if val not in ("", "0", "false", "no"):
            flag_categories.append(cat)
            add(f"addoninfo flag: {key}={val} -> {cat}")
            mark(key.replace("addoncontent_", ""))

    if "danyria" in hay or any("danyria" in r for r in rels):
        add("Decision: Danyria name/path matched.")
        return "Danyria", sorted(set(tags)), evidence

    if mission_count > 0 and bsp_count > 0:
        add("Decision: Campaign wins because missions/* and maps/*.bsp are both present.")
        return "Campaign", sorted(set(tags)), evidence
    if bsp_count > 0:
        add("Decision: Map wins because maps/*.bsp is present.")
        return "Map", sorted(set(tags)), evidence

    if sound_total > 0 and decisive_non_sound_total == 0:
        add("Decision: Sound / Music wins because this is a sound-only mod; all sound subtypes are unified.")
        return "Sound / Music", sorted(set(tags)), evidence

    if medical_visual_count > 0:
        add("Decision: Medical / Items wins by medkit/pills/adrenaline/defib visual or script signature.")
        return "Medical / Items", sorted(set(tags)), evidence
    if throwable_visual_count > 0:
        add("Decision: Throwables wins by molotov/pipe bomb/vomitjar visual or script signature.")
        return "Throwables", sorted(set(tags)), evidence
    if carryable_visual_count > 0:
        add("Decision: Carryables / Props wins by gascan/propane/cola/gnome/carryable signature.")
        return "Carryables / Props", sorted(set(tags)), evidence
    if weapon_decisive_total > 0:
        add("Decision: Weapon wins by model/material/item-script replacement signature.")
        return "Weapon", sorted(set(tags)), evidence
    if survivor_model_count > 0:
        add("Decision: Character / Skin wins by survivor model/material paths.")
        return "Character / Skin", sorted(set(tags)), evidence
    if infected_model_count > 0:
        add("Decision: Infected wins by infected model/material paths.")
        return "Infected", sorted(set(tags)), evidence
    if ui_count > 0:
        add("Decision: HUD / UI wins by UI resource paths.")
        return "HUD / UI", sorted(set(tags)), evidence
    if vscript_count > 0:
        add("Decision: addon / Script wins by vscripts/modes/.nut paths.")
        return "Mutation / Script", sorted(set(tags)), evidence
    if prop_model_count > 0:
        add("Decision: Carryables / Props wins by prop/vehicle model paths.")
        return "Carryables / Props", sorted(set(tags)), evidence
    if effect_count > 0:
        add("Decision: Effects / Particles wins by particle/effect paths.")
        return "Effects / Particles", sorted(set(tags)), evidence
    if sound_total > 0:
        add("Decision: Sound / Music wins because sound resources are present and no higher-priority visual replacement was chosen.")
        return "Sound / Music", sorted(set(tags)), evidence
    if texture_only_count > 0:
        add("Decision: Texture / Materials wins by material-only paths.")
        return "Texture / Materials", sorted(set(tags)), evidence

    for cat in ["Sound / Music", "Weapon", "Character / Skin", "Infected", "HUD / UI", "Mutation / Script", "Campaign", "Map"]:
        if cat in flag_categories:
            if cat in ("Campaign", "Map"):
                add("Decision: weak fallback from addoninfo only; no real map/campaign files found.")
            else:
                add("Decision: fallback from addoninfo content flag.")
            return cat, sorted(set(tags)), evidence

    title_keywords = [
        ("Medical / Items", [" medkit ", " first aid ", " first_aid ", " pills ", " pain pills ", " adrenaline ", " defib ", " defibrillator "]),
        ("Throwables", [" molotov ", " pipe bomb ", " pipe_bomb ", " vomitjar ", " bile "]),
        ("Carryables / Props", [" gascan ", " propane ", " oxygen tank ", " cola ", " gnome "]),
        ("Sound / Music", [" sound ", " music ", " voice ", " audio ", " bgm ", " firing sound ", " reload sound ", " weapon sound "]),
        ("Weapon", [" weapon ", " rifle ", " shotgun ", " pistol ", " smg ", " sniper ", " melee ", " m16 ", " ak47 ", " ak-47 ", " deagle ", " magnum ", " katana ", " machete "]),
        ("HUD / UI", [" hud ", " ui ", " crosshair ", " menu ", " interface "]),
        ("Mutation / Script", [" addon ", " vscript ", " script ", " director "]),
        ("Character / Skin", [" survivor ", " skin ", " ellis ", " nick ", " coach ", " rochelle ", " zoey ", " bill ", " louis ", " francis "]),
        ("Infected", [" infected ", " witch ", " tank ", " hunter ", " smoker ", " boomer ", " charger ", " spitter ", " jockey "]),
        ("Campaign", [" campaign ", " chapter ", " finale "]),
        ("Map", [" survival map ", " map "]),
    ]
    for cat, keys in title_keywords:
        if any(k in hay for k in keys):
            add(f"Decision: weak title keyword fallback -> {cat}")
            return cat, sorted(set(tags)), evidence

    add("Decision: Unknown; no decisive file-tree signature.")
    return "Unknown", sorted(set(tags)), evidence


def scan_one(path: Path, l4d2: Path) -> Optional[ModRecord]:
    low = path.name.lower()
    enabled = not low.endswith(".disabled")
    status = "Enabled" if enabled else "Disabled"
    source = source_for(path, l4d2)

    if path.is_file():
        is_disabled_vpk = low.endswith(".vpk.disabled")
        looks_vpk = path.suffix.lower() == ".vpk" or is_disabled_vpk or is_vpk_magic(path)
        if not looks_vpk:
            return None

        fallback_title = path.name
        for suf in [".vpk.disabled", ".disabled", ".vpk"]:
            if fallback_title.lower().endswith(suf):
                fallback_title = fallback_title[:-len(suf)]
                break

        workshop_id = fallback_title if fallback_title.isdigit() else ""
        rels, entries, valid, note, data_base = parse_vpk(path)
        addoninfo = {}
        title = fallback_title
        author = ""
        desc = ""

        raw_info = read_vpk_file(path, entries, data_base, "addoninfo.txt")
        if not raw_info:
            raw_info = read_vpk_file(path, entries, data_base, "addoninfo")
        if raw_info:
            txt = raw_info.decode("utf-8", errors="replace")
            addoninfo = parse_keyvalues_flat(txt)
            title = addoninfo.get("addontitle", title)
            author = addoninfo.get("addonauthor", "")
            desc = addoninfo.get("addondescription", addoninfo.get("addontagline", ""))
        elif workshop_id:
            title = f"Workshop {workshop_id}"

        category, tags, evidence = classify_mod(title, desc, addoninfo, rels)
        evidence.insert(0, f"VPK: {note}")
        if raw_info:
            evidence.insert(1, "read addoninfo.txt inside VPK")
        if not valid:
            category = "Unknown"
            status = "Broken"

        return ModRecord(title, category, "VPK", source, status, str(path), file_size_mb(path), author, desc, modified_str(path), tags, evidence, valid, workshop_id)

    if path.is_dir():
        title = path.name
        author = ""
        desc = ""
        addoninfo = {}
        info = path / "addoninfo.txt"
        if info.exists():
            addoninfo = parse_keyvalues_flat(read_text_safe(info))
            title = addoninfo.get("addontitle", title)
            author = addoninfo.get("addonauthor", "")
            desc = addoninfo.get("addondescription", addoninfo.get("addontagline", ""))

        rels = []
        try:
            for p in path.rglob("*"):
                if p.is_file():
                    rels.append(str(p.relative_to(path)).replace("\\", "/").lower())
                    if len(rels) >= 40000:
                        break
        except Exception:
            pass
        category, tags, evidence = classify_mod(title, desc, addoninfo, rels)
        workshop_id = path.name if source == "Workshop" and path.name.isdigit() else ""
        if workshop_id:
            evidence.insert(0, f"Workshop ID from folder name: {workshop_id}")
        return ModRecord(title, category, "Folder", source, status, str(path), folder_size_mb(path), author, desc, modified_str(path), tags, evidence, True, workshop_id)
    return None

def find_steam_libraries() -> list[Path]:
    # 中文：尽量从注册表、常见目录和 libraryfolders.vdf 找到所有 Steam 库。
    # English: Find Steam libraries from registry, common folders, and libraryfolders.vdf.
    candidates: list[Path] = []
    for base in [os.environ.get("ProgramFiles(x86)"), os.environ.get("ProgramFiles")]:
        if base:
            candidates.append(Path(base) / "Steam")
    if os.name == "nt":
        try:
            import winreg
            for hive, subkey in (
                (winreg.HKEY_CURRENT_USER, r"Software\Valve\Steam"),
                (winreg.HKEY_LOCAL_MACHINE, r"Software\Wow6432Node\Valve\Steam"),
                (winreg.HKEY_LOCAL_MACHINE, r"Software\Valve\Steam"),
            ):
                try:
                    with winreg.OpenKey(hive, subkey) as key:
                        for value_name in ("SteamPath", "InstallPath"):
                            try:
                                value, _ = winreg.QueryValueEx(key, value_name)
                                if value:
                                    candidates.append(Path(str(value)))
                            except Exception:
                                pass
                except Exception:
                    pass
        except Exception:
            pass
    for drive in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
        candidates += [Path(f"{drive}:\\Steam"), Path(f"{drive}:\\SteamLibrary")]
    libs: list[Path] = []
    seen = set()
    queue: list[Path] = []
    for steam in candidates:
        try:
            if not steam.exists():
                continue
        except Exception:
            continue
        queue.append(steam)
    while queue:
        steam = queue.pop(0)
        try:
            k = str(steam.resolve()).lower()
        except Exception:
            k = str(steam).lower()
        if k in seen:
            continue
        seen.add(k)
        libs.append(steam)
        vdf = steam / "steamapps" / "libraryfolders.vdf"
        if vdf.exists():
            txt = read_text_safe(vdf)
            for m in re.finditer(r'"path"\s+"([^"]+)"', txt):
                p = Path(m.group(1).replace("\\\\", "\\"))
                try:
                    pk = str(p.resolve()).lower()
                except Exception:
                    pk = str(p).lower()
                if pk not in seen:
                    queue.append(p)
    return libs

def candidate_l4d2_paths() -> list[Path]:
    out = []
    for lib in find_steam_libraries():
        out.append(lib / "steamapps" / "common" / "Left 4 Dead 2" / "left4dead2")
    for drive in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
        out.append(Path(f"{drive}:\\SteamLibrary\\steamapps\\common\\Left 4 Dead 2\\left4dead2"))
        out.append(Path(f"{drive}:\\Steam\\steamapps\\common\\Left 4 Dead 2\\left4dead2"))
    seen, clean = set(), []
    for p in out:
        k = str(p).lower()
        if k not in seen:
            seen.add(k); clean.append(p)
    return clean

# ---------------------------------------------------------------------------
# 自绘控件和视觉效果控件。
# Custom painted widgets and visual-effect widgets.
# ---------------------------------------------------------------------------
class ImageLabel(QLabel):
    _pixmap_cache = {}

    def __init__(self, max_w: int, max_h: int, fallback: str):
        super().__init__(fallback)
        self.max_w = max_w
        self.max_h = max_h
        self.original: Optional[QPixmap] = None
        self.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        self.setScaledContents(False)

    def _crop_transparent(self, px: QPixmap) -> QPixmap:
        try:
            img = px.toImage()
            w = img.width()
            h = img.height()
            if w <= 0 or h <= 0:
                return px

            left, right, top, bottom = w, -1, h, -1
            for y in range(h):
                for x in range(w):
                    if img.pixelColor(x, y).alpha() > 6:
                        if x < left:
                            left = x
                        if x > right:
                            right = x
                        if y < top:
                            top = y
                        if y > bottom:
                            bottom = y

            if right < left or bottom < top:
                return px

            pad = 4
            left = max(0, left - pad)
            top = max(0, top - pad)
            right = min(w - 1, right + pad)
            bottom = min(h - 1, bottom + pad)
            return px.copy(left, top, right - left + 1, bottom - top + 1)
        except Exception:
            return px

    def set_image(self, path: Path) -> bool:
        if not path.exists():
            return False

        try:
            stat = path.stat()
            cache_key = (str(path.resolve()).lower(), stat.st_mtime_ns, stat.st_size, self.max_w, self.max_h, "raw_full_png")
        except Exception:
            cache_key = (str(path).lower(), self.max_w, self.max_h, "raw_full_png")

        if cache_key in ImageLabel._pixmap_cache:
            self.original = ImageLabel._pixmap_cache[cache_key]
        else:
            px = QPixmap(str(path))
            if px.isNull():
                return False

            self.original = px
            ImageLabel._pixmap_cache[cache_key] = self.original

        self.setText("")
        self.repaint_image()
        return True

    def resizeEvent(self, e):
        super().resizeEvent(e)
        self.repaint_image()

    def repaint_image(self):
        if not self.original:
            return

        target_w = max(1, min(max(1, self.width()), self.max_w))
        target_h = max(1, min(max(1, self.height()), self.max_h))
        scaled = self.original.scaled(
            QSize(target_w, target_h),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
        self.setPixmap(scaled)


class BrandLogoWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.title_text = "DANYRIA"
        self.version_label = "VERSION"
        self.version_text = f"{self.version_label} {APP_VERSION}"
        self.title_color = QColor("#6FADE8")
        self.version_color = QColor("#EA6FBE")
        self.title_px = 35
        self.version_px = 12
        self.tracking = 2.5
        self.setMinimumSize(230, 52)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

    def set_theme_colors(self, title_color: str, version_color: str):
        self.title_color = QColor(title_color)
        self.version_color = QColor(version_color)
        self.update()

    def set_version(self, version: str, label: str | None = None):
        if label:
            self.version_label = label
        self.version_text = f"{self.version_label} {version}"
        self.update()

    def _font(self, px_size: int, weight=QFont.Weight.DemiBold):
        f = QFont("Bahnschrift SemiBold")
        f.setStyleStrategy(QFont.StyleStrategy.PreferAntialias)
        f.setPixelSize(px_size)
        f.setWeight(weight)
        return f

    def sizeHint(self):
        return QSize(300, 54)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        painter.setRenderHint(QPainter.RenderHint.TextAntialiasing, True)

        left = 0.0

        title_font = self._font(self.title_px, QFont.Weight.DemiBold)
        version_font = self._font(self.version_px, QFont.Weight.DemiBold)

        title_fm = QFontMetrics(title_font)
        version_fm = QFontMetrics(version_font)

        title_base = 34
        version_base = 52

        title_x = left
        version_x = left + 2

        painter.setFont(title_font)
        painter.setPen(self.title_color)

        x = title_x
        for ch in self.title_text:
            painter.drawText(int(round(x)), title_base, ch)
            x += title_fm.horizontalAdvance(ch) + self.tracking

        painter.setFont(version_font)
        painter.setPen(self.version_color)
        painter.drawText(int(round(version_x)), version_base, self.version_text)

        painter.end()


class DrawnIconButton(QPushButton):
    def __init__(self, icon_kind: str, parent=None):
        super().__init__(parent)
        self.icon_kind = icon_kind
        self.setText("")
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setProperty("drawnIcon", True)

    def set_icon_kind(self, icon_kind: str):
        self.icon_kind = icon_kind
        self.update()

    def _colors(self):
        w = self.window()
        theme = getattr(w, "theme_key", "normal")
        t = THEMES.get(theme, THEMES["normal"])
        base = QColor(t.get("muted", "#65748D"))
        accent = QColor(t.get("accent", "#7DBDFF"))
        danger = QColor(t.get("danger", "#D96A9A"))
        bg = QColor(t.get("chip", "#EAF3FF"))
        return base, accent, danger, bg

    def paintEvent(self, event):
        base, accent, danger, bg = self._colors()
        r = self.rect().adjusted(3, 3, -3, -3)

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

        if self.underMouse():
            fill = QColor(bg)
            fill.setAlpha(180)
            painter.setBrush(QBrush(fill))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawRoundedRect(r, 9, 9)

        color = danger if self.icon_kind == "close" and self.underMouse() else (accent if self.underMouse() else base)
        pen = QPen(color, 1.8, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin)
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)

        cx = self.width() / 2
        cy = self.height() / 2

        if self.icon_kind == "settings":
            radius = min(self.width(), self.height()) * 0.20
            inner = radius * 0.42
            import math
            for i in range(8):
                a = math.radians(i * 45)
                x1 = cx + math.cos(a) * (radius + 1)
                y1 = cy + math.sin(a) * (radius + 1)
                x2 = cx + math.cos(a) * (radius + 5)
                y2 = cy + math.sin(a) * (radius + 5)
                painter.drawLine(QPointF(x1, y1), QPointF(x2, y2))
            painter.drawEllipse(QPointF(cx, cy), radius, radius)
            painter.drawEllipse(QPointF(cx, cy), inner, inner)

        elif self.icon_kind == "minimize":
            painter.drawLine(QPointF(cx - 7, cy), QPointF(cx + 7, cy))

        elif self.icon_kind == "maximize":
            painter.drawRoundedRect(int(cx - 7), int(cy - 7), 14, 14, 2, 2)

        elif self.icon_kind == "restore":
            painter.drawRoundedRect(int(cx - 4), int(cy - 8), 12, 12, 2, 2)
            painter.drawRoundedRect(int(cx - 8), int(cy - 4), 12, 12, 2, 2)

        elif self.icon_kind == "close":
            painter.drawLine(QPointF(cx - 6, cy - 6), QPointF(cx + 6, cy + 6))
            painter.drawLine(QPointF(cx + 6, cy - 6), QPointF(cx - 6, cy + 6))

        painter.end()


class CollapsibleSection(QFrame):
    def __init__(self, title: str, subtitle: str = "", parent=None, expanded: bool = True):
        super().__init__(parent)
        self.setObjectName("TableCard")
        self._expanded = expanded
        self._title = title
        self._subtitle = subtitle
        self._animations = []

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        self.header_wrap = QFrame()
        self.header_wrap.setObjectName("CollapsibleHeaderFrame")
        header_l = QHBoxLayout(self.header_wrap)
        header_l.setContentsMargins(0, 0, 12, 0)
        header_l.setSpacing(8)
        self.header = QPushButton()
        self.header.setObjectName("CollapsibleHeader")
        self.header.setCursor(Qt.CursorShape.PointingHandCursor)
        self.header.clicked.connect(self.toggle)
        header_l.addWidget(self.header, 1)
        self.status_badge = QLabel("")
        self.status_badge.setObjectName("Pill")
        self.status_badge.setVisible(False)
        header_l.addWidget(self.status_badge, 0, Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignTop)
        root.addWidget(self.header_wrap)

        self.body = QWidget()
        self.body_l = QVBoxLayout(self.body)
        self.body_l.setContentsMargins(18, 4, 18, 16)
        self.body_l.setSpacing(12)
        root.addWidget(self.body)
        self.body.setVisible(expanded)
        self.body.setMaximumHeight(16777215 if expanded else 0)
        self.sync_header()

    def set_title(self, title: str, subtitle: str = None):
        self._title = title
        if subtitle is not None:
            self._subtitle = subtitle
        self.sync_header()

    def set_status_text(self, text: str):
        self.status_badge.setText(text or "")
        self.status_badge.setVisible(bool((text or "").strip()))

    def toggle(self):
        self.set_expanded(not self._expanded, animated=True)

    def set_expanded(self, expanded: bool, animated: bool = False):
        if self._expanded == expanded and self.body.isVisible() == expanded:
            self.sync_header()
            return
        self._expanded = expanded
        self.sync_header()
        if not animated:
            self.body.setVisible(expanded)
            self.body.setMaximumHeight(16777215 if expanded else 0)
            return

        try:
            effect = self.body.graphicsEffect()
            if not isinstance(effect, QGraphicsOpacityEffect):
                effect = QGraphicsOpacityEffect(self.body)
                self.body.setGraphicsEffect(effect)
            self.body.setVisible(True)
            end_height = max(1, self.body.sizeHint().height())
            start_height = 0 if expanded else max(self.body.height(), end_height)
            self.body.setMaximumHeight(start_height)

            height_anim = QPropertyAnimation(self.body, b"maximumHeight", self)
            height_anim.setDuration(190)
            height_anim.setStartValue(start_height)
            height_anim.setEndValue(end_height if expanded else 0)
            height_anim.setEasingCurve(QEasingCurve(QEasingCurve.Type.OutCubic))

            opacity_anim = QPropertyAnimation(effect, b"opacity", self)
            opacity_anim.setDuration(150)
            opacity_anim.setStartValue(0.0 if expanded else 1.0)
            opacity_anim.setEndValue(1.0 if expanded else 0.0)
            opacity_anim.setEasingCurve(QEasingCurve(QEasingCurve.Type.OutCubic))

            def finish():
                if self._expanded:
                    self.body.setMaximumHeight(16777215)
                else:
                    self.body.setVisible(False)
                    self.body.setMaximumHeight(0)

            height_anim.finished.connect(finish)
            self.keep_animation(height_anim)
            self.keep_animation(opacity_anim)
        except Exception:
            self.body.setVisible(expanded)
            self.body.setMaximumHeight(16777215 if expanded else 0)

    def keep_animation(self, anim):
        self._animations.append(anim)
        anim.finished.connect(lambda a=anim: self._animations.remove(a) if a in self._animations else None)
        anim.start()

    def sync_header(self):
        arrow = "▾" if self._expanded else "▸"
        sub = (self._subtitle or "").strip()
        if sub:
            self.header.setText(f"{arrow}  {self._title}\n{sub}")
        else:
            self.header.setText(f"{arrow}  {self._title}")

class TitleBar(QFrame):
    def __init__(self, window):
        super().__init__()
        self.window_ref = window
        self.setObjectName("TitleBar")
        self.drag_pos = None

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            try:
                self.window().windowHandle().startSystemMove()
                event.accept()
                return
            except Exception:
                self.drag_pos = event.globalPosition().toPoint() if hasattr(event, "globalPosition") else event.globalPos()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.drag_pos is not None and event.buttons() & Qt.MouseButton.LeftButton:
            pos = event.globalPosition().toPoint() if hasattr(event, "globalPosition") else event.globalPos()
            delta = pos - self.drag_pos
            self.window().move(self.window().pos() + delta)
            self.drag_pos = pos
            event.accept()
            return
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        self.drag_pos = None
        super().mouseReleaseEvent(event)


class DanyriaDialog(QDialog):
    BUTTON_TEXT = {
        "zh": {"ok": "确定", "yes": "是", "no": "否"},
        "en": {"ok": "OK", "yes": "Yes", "no": "No"},
        "ja": {"ok": "OK", "yes": "はい", "no": "いいえ"},
        "ko": {"ok": "확인", "yes": "예", "no": "아니오"},
        "ru": {"ok": "OK", "yes": "Да", "no": "Нет"},
        "de": {"ok": "OK", "yes": "Ja", "no": "Nein"},
        "fr": {"ok": "OK", "yes": "Oui", "no": "Non"},
        "es": {"ok": "OK", "yes": "Sí", "no": "No"},
    }

    def __init__(self, parent, title: str, text: str, level: str = "info", buttons=None):
        super().__init__(parent)
        self.result_button = NativeQMessageBox.StandardButton.No
        self._drag_pos = None
        self.parent_window = parent
        self.theme_key = getattr(parent, "theme_key", "normal")
        self.t = THEMES.get(self.theme_key, THEMES["normal"])
        self._animations = []
        self._shown_once = False
        self.setModal(True)
        self.setWindowTitle(title or APP_NAME)
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setWindowOpacity(0.0)
        self.setMinimumWidth(440)
        self.setMaximumWidth(720)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(10, 10, 10, 10)
        outer.setSpacing(0)

        frame = QFrame()
        frame.setObjectName("WindowFrame")
        outer.addWidget(frame)
        root = QVBoxLayout(frame)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        titlebar = QFrame()
        titlebar.setObjectName("TitleBar")
        titlebar.setFixedHeight(48)
        titlebar.setMouseTracking(True)
        titlebar.mousePressEvent = self._title_mouse_press
        titlebar.mouseMoveEvent = self._title_mouse_move
        titlebar.mouseReleaseEvent = self._title_mouse_release
        title_l = QHBoxLayout(titlebar)
        title_l.setContentsMargins(18, 8, 12, 8)
        title_l.setSpacing(10)
        brand = QLabel(APP_NAME.upper())
        brand.setObjectName("DialogBrand")
        title_label = QLabel(title or APP_NAME)
        title_label.setObjectName("DialogTitle")
        title_label.setMinimumWidth(220)
        title_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        close_btn = DrawnIconButton("close")
        close_btn.setObjectName("CloseButton")
        close_btn.setProperty("windowButton", True)
        close_btn.setFixedSize(30, 30)
        close_btn.clicked.connect(self._close_from_title)
        title_l.addWidget(brand)
        title_l.addWidget(title_label, 1)
        title_l.addWidget(close_btn)
        root.addWidget(titlebar)

        body = QWidget()
        body_l = QVBoxLayout(body)
        body_l.setContentsMargins(24, 18, 24, 20)
        body_l.setSpacing(16)

        top = QHBoxLayout()
        badge = QLabel("!" if level == "warning" else "i")
        badge.setObjectName("DialogBadgeWarning" if level == "warning" else "DialogBadgeInfo")
        badge.setFixedSize(30, 30)
        badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        msg = QLabel(str(text or ""))
        msg.setObjectName("DialogMessage")
        msg.setWordWrap(True)
        msg.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        msg.setMinimumWidth(360)
        top.addWidget(badge, 0, Qt.AlignmentFlag.AlignTop)
        top.addWidget(msg, 1)
        body_l.addLayout(top)

        btn_l = QHBoxLayout()
        btn_l.addStretch(1)
        buttons = buttons or ["ok"]
        for button_key in buttons:
            b = QPushButton(self._button_text(button_key))
            if button_key in ("ok", "yes"):
                b.setProperty("accent", True)
            b.setMinimumWidth(92)
            b.clicked.connect(lambda checked=False, k=button_key: self._finish(k))
            btn_l.addWidget(b)
        body_l.addLayout(btn_l)
        root.addWidget(body)

        self.setStyleSheet(self._dialog_qss())
        self.adjustSize()

    def _button_text(self, key: str) -> str:
        lang = "en"
        try:
            if self.parent_window and hasattr(self.parent_window, "current_language"):
                lang = self.parent_window.current_language()
        except Exception:
            lang = "en"
        return self.BUTTON_TEXT.get(lang, self.BUTTON_TEXT["en"]).get(key, key)

    def _dialog_qss(self) -> str:
        t = self.t
        return f"""
QDialog {{
    background: transparent;
    color: {t['text']};
    font-family: "Microsoft YaHei UI", "Segoe UI";
    font-size: 12px;
}}
QFrame#WindowFrame {{
    background: {t['panel']};
    border: 1px solid {t['line']};
    border-radius: 18px;
}}
QFrame#TitleBar {{
    background: {t['bg']};
    border-top-left-radius: 18px;
    border-top-right-radius: 18px;
}}
QLabel#DialogBrand {{
    background: transparent;
    color: {t['brand_title']};
    font-family: "Bahnschrift SemiBold", "Segoe UI Semibold", "Microsoft YaHei UI";
    font-size: 14px;
    font-weight: 900;
    letter-spacing: 2px;
}}
QLabel#DialogTitle {{
    background: transparent;
    color: {t['text']};
    font-size: 13px;
    font-weight: 800;
}}
QLabel#DialogMessage {{
    background: transparent;
    color: {t['text']};
    font-size: 12px;
    font-weight: 600;
    line-height: 1.5;
}}
QLabel#DialogBadgeInfo {{
    background: {t['chip']};
    color: {t['chip_text']};
    border: 1px solid {t['line']};
    border-radius: 15px;
    font-weight: 900;
}}
QLabel#DialogBadgeWarning {{
    background: {t['danger']};
    color: #FFFFFF;
    border: 0px;
    border-radius: 15px;
    font-weight: 900;
}}
QPushButton {{
    background: {t['panel2']};
    border: 1px solid {t['line']};
    border-radius: 11px;
    padding: 8px 14px;
    color: {t['text']};
    font-weight: 800;
}}
QPushButton:hover {{
    border-color: {t['accent']};
}}
QPushButton[accent="true"] {{
    background: {t['accent']};
    color: #10131A;
    border: 0px;
}}
QPushButton[windowButton="true"] {{
    background: transparent;
    border: 0px;
    padding: 4px;
    border-radius: 8px;
}}
QPushButton[windowButton="true"]:hover {{
    background: {t['danger']};
    color: #FFFFFF;
}}
"""

    def _title_mouse_press(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            try:
                self.windowHandle().startSystemMove()
                event.accept()
                return
            except Exception:
                self._drag_pos = event.globalPosition().toPoint() if hasattr(event, "globalPosition") else event.globalPos()
                event.accept()
                return
        event.ignore()

    def _title_mouse_move(self, event):
        if self._drag_pos is not None and event.buttons() & Qt.MouseButton.LeftButton:
            pos = event.globalPosition().toPoint() if hasattr(event, "globalPosition") else event.globalPos()
            self.move(self.pos() + (pos - self._drag_pos))
            self._drag_pos = pos
            event.accept()
            return
        event.ignore()

    def _title_mouse_release(self, event):
        self._drag_pos = None
        event.accept()

    def _close_from_title(self):
        self._finish("no")

    def _finish(self, key: str):
        if key == "yes":
            self.result_button = NativeQMessageBox.StandardButton.Yes
        elif key == "no":
            self.result_button = NativeQMessageBox.StandardButton.No
        else:
            self.result_button = NativeQMessageBox.StandardButton.Ok
        self.accept()

    def showEvent(self, event):
        super().showEvent(event)
        try:
            if self.parent() is not None:
                pg = self.parent().frameGeometry()
                self.move(pg.center() - self.rect().center())
        except Exception:
            pass
        if self._shown_once:
            return
        self._shown_once = True
        try:
            final_pos = self.pos()
            self.move(final_pos + QPoint(0, 10))

            pos_anim = QPropertyAnimation(self, b"pos", self)
            pos_anim.setDuration(170)
            pos_anim.setStartValue(self.pos())
            pos_anim.setEndValue(final_pos)
            pos_anim.setEasingCurve(QEasingCurve(QEasingCurve.Type.OutCubic))

            opacity_anim = QPropertyAnimation(self, b"windowOpacity", self)
            opacity_anim.setDuration(150)
            opacity_anim.setStartValue(0.0)
            opacity_anim.setEndValue(1.0)
            opacity_anim.setEasingCurve(QEasingCurve(QEasingCurve.Type.OutCubic))

            self.keep_animation(pos_anim)
            self.keep_animation(opacity_anim)
        except Exception:
            try:
                self.setWindowOpacity(1.0)
            except Exception:
                pass

    def keep_animation(self, anim):
        self._animations.append(anim)
        anim.finished.connect(lambda a=anim: self._animations.remove(a) if a in self._animations else None)
        anim.start()


class DanyriaMessageBox:
    StandardButton = NativeQMessageBox.StandardButton

    @staticmethod
    def information(parent, title, text, *args, **kwargs):
        dlg = DanyriaDialog(parent, title, text, "info", ["ok"])
        try:
            dlg.exec()
        except AttributeError:
            dlg.exec_()
        return dlg.result_button

    @staticmethod
    def warning(parent, title, text, *args, **kwargs):
        dlg = DanyriaDialog(parent, title, text, "warning", ["ok"])
        try:
            dlg.exec()
        except AttributeError:
            dlg.exec_()
        return dlg.result_button

    @staticmethod
    def question(parent, title, text, *args, **kwargs):
        dlg = DanyriaDialog(parent, title, text, "warning", ["yes", "no"])
        try:
            dlg.exec()
        except AttributeError:
            dlg.exec_()
        return dlg.result_button


QMessageBox = DanyriaMessageBox


class CursorFxOverlay(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setAutoFillBackground(False)

        self.trail_points = []
        self.trail_color = QColor(125, 189, 255)
        self.wash_color = QColor(125, 189, 255)
        self.wash_age = 9999
        self.wash_life = 360
        self._last_trail_ms = 0
        self._last_pos = None

        self.timer = QTimer(self)
        self.timer.setInterval(40)
        self.timer.timeout.connect(self.tick)
        self.timer.start()
        self.hide()

    def now_ms(self):
        return int(time.time() * 1000)

    def set_theme(self, theme_key: str, theme: dict):
        if theme_key == "ruin":
            self.trail_color = QColor(theme.get("accent2", "#9A69FF"))
            self.wash_color = QColor(theme.get("accent2", "#9A69FF"))
        else:
            self.trail_color = QColor(theme.get("accent", "#7DBDFF"))
            self.wash_color = QColor(theme.get("accent", "#7DBDFF"))

    def add_trail(self, pos):
        now = self.now_ms()
        p = QPointF(pos)

        if self._last_pos is not None:
            dx = p.x() - self._last_pos.x()
            dy = p.y() - self._last_pos.y()
            if dx * dx + dy * dy < 24 and now - self._last_trail_ms < 36:
                return

        if now - self._last_trail_ms < 28:
            return

        self._last_trail_ms = now
        self._last_pos = p
        self.show()
        self.raise_()
        self.trail_points.append((p, now))

        cutoff = now - 240
        self.trail_points = [(pt, ts) for pt, ts in self.trail_points if ts >= cutoff]
        if len(self.trail_points) > 16:
            self.trail_points = self.trail_points[-16:]
        self.update()

    def add_click(self, pos):
        return

    def add_theme_wash(self):
        self.show()
        self.raise_()
        self.wash_age = 0
        self.update()

    def tick(self):
        now = self.now_ms()
        self.trail_points = [(pt, ts) for pt, ts in self.trail_points if now - ts <= 240]

        if self.wash_age < self.wash_life:
            self.wash_age += 16

        if self.trail_points or self.wash_age < self.wash_life:
            self.update()
        else:
            self.hide()

    def paintEvent(self, event):
        now = self.now_ms()
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

        if self.wash_age < self.wash_life:
            ratio = min(1.0, self.wash_age / max(1, self.wash_life))
            color = QColor(self.wash_color)
            color.setAlpha(int(78 * (1.0 - ratio)))
            pen = QPen(color, 1.8 + 1.4 * (1.0 - ratio))
            pen.setCapStyle(Qt.PenCapStyle.FlatCap)
            painter.setPen(pen)
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawRoundedRect(self.rect().adjusted(5, 5, -6, -6), 17, 17)

        pts = [(pt, ts) for pt, ts in self.trail_points if now - ts <= 240]
        if len(pts) >= 2:
            for i in range(1, len(pts)):
                p0, t0 = pts[i - 1]
                p1, t1 = pts[i]
                age = now - ((t0 + t1) // 2)
                ratio = min(1.0, max(0.0, age / 240.0))
                color = QColor(self.trail_color)
                color.setAlpha(max(0, int(120 * (1.0 - ratio))))
                width = 2.1 * (1.0 - ratio) + 0.45
                pen = QPen(color, width, Qt.PenStyle.SolidLine, Qt.PenCapStyle.FlatCap, Qt.PenJoinStyle.MiterJoin)
                painter.setPen(pen)
                painter.drawLine(p0, p1)

        painter.end()


# ---------------------------------------------------------------------------
# 武器脚本解析与参考性能估算。
# Weapon script parsing and rough performance simulation.
# ---------------------------------------------------------------------------
WEAPON_VALUE_RE = re.compile(r'^(?P<prefix>\s*"(?P<key>[^"]+)"\s+"?)(?P<value>[-+]?\d+(?:\.\d+)?)(?P<suffix>"?.*)$')
WEAPON_NUMBER_RE = re.compile(r'^[-+]?\d+(?:\.\d+)?$')

OFFICIAL_GUN_SCRIPT_NAMES = {
    "weapon_autoshotgun.txt", "weapon_grenade_launcher.txt", "weapon_hunting_rifle.txt",
    "weapon_pistol.txt", "weapon_pistol_magnum.txt", "weapon_pumpshotgun.txt",
    "weapon_rifle.txt", "weapon_rifle_ak47.txt", "weapon_rifle_desert.txt",
    "weapon_rifle_m60.txt", "weapon_rifle_sg552.txt", "weapon_shotgun_chrome.txt",
    "weapon_shotgun_spas.txt", "weapon_smg.txt", "weapon_smg_mp5.txt",
    "weapon_smg_silenced.txt", "weapon_sniper_awp.txt", "weapon_sniper_military.txt",
    "weapon_sniper_scout.txt",
}
OFFICIAL_SPECIAL_MELEE_SCRIPT_NAMES = {"weapon_chainsaw.txt"}
OFFICIAL_MELEE_SCRIPT_NAMES = {
    "baseball_bat.txt", "cricket_bat.txt", "crowbar.txt", "electric_guitar.txt",
    "fireaxe.txt", "frying_pan.txt", "golfclub.txt", "golf_club.txt", "katana.txt",
    "knife.txt", "machete.txt", "pitchfork.txt", "shovel.txt", "tonfa.txt",
}
OFFICIAL_MELEE_NAME_ALIASES = {"golf_club": "golfclub"}

PARAM_KEY_TO_I18N = {
    "damage": "param_damage", "damageperhit": "param_damageperhit",
    "bullets": "param_bullets", "pellets": "param_pellets", "pelletcount": "param_pellets", "numshots": "param_bullets",
    "cycletime": "param_cycletime", "refiredelay": "param_refiredelay", "fireinterval": "param_cycletime",
    "attackinterval": "param_attackinterval", "swingtime": "param_swingtime",
    "clipsize": "param_clipsize", "clip": "param_clipsize", "defaultclip": "param_defaultclip", "maxclip": "param_maxclip",
    "reloadduration": "param_reloadduration", "reloadtime": "param_reloadtime", "reload": "param_reloadtime",
    "reloademptyduration": "param_reloademptyduration", "deployduration": "param_deployduration",
    "maxplayerspeed": "param_maxplayerspeed", "weaponarmorratio": "param_weaponarmorratio",
    "verticalpunch": "param_verticalpunch", "punchangle": "param_punchangle", "recoil": "param_recoil",
    "spreadpershot": "param_spreadpershot", "maxspread": "param_maxspread", "spreaddecay": "param_spreaddecay",
    "minstandingspread": "param_minstandingspread", "minduckingspread": "param_minduckingspread",
    "mininairspread": "param_mininairspread", "maxmovementspread": "param_maxmovementspread", "aimingspread": "param_aimingspread",
    "range": "param_range", "rangemodifier": "param_rangemodifier", "swingrange": "param_swingrange",
    "crosshairmindistance": "param_crosshairmindistance", "crosshairdeltadistance": "param_crosshairdeltadistance",
    "penetrationnumlayers": "param_penetrationnumlayers", "penetrationpower": "param_penetrationpower",
    "rumble": "param_rumble", "bucket": "param_bucket", "bucketposition": "param_bucketposition",
    "tier": "param_tier", "weapontier": "param_tier",
    "weight": "param_weight", "itemflags": "param_itemflags", "damageflags": "param_damageflags",
    "duration": "param_duration", "startdir": "param_startdir", "enddir": "param_enddir",
    "starttime": "param_starttime", "endtime": "param_endtime", "force": "param_force", "forcedir": "param_forcedir",
}


def normalize_script_key(key: str) -> str:
    return str(key).lower().replace(" ", "").replace("_", "")


def weapon_param_i18n_key(key: str) -> str:
    return PARAM_KEY_TO_I18N.get(normalize_script_key(key), "weapon_param_generic")


def _weapon_rel(rel: str) -> str:
    return str(rel).lower().replace("\\", "/").strip("/")


def weapon_name_key_from_rel(rel: str) -> str:
    r = _weapon_rel(rel)
    name = Path(r).name.lower()
    stem = Path(name).stem
    if name in OFFICIAL_GUN_SCRIPT_NAMES or name in OFFICIAL_SPECIAL_MELEE_SCRIPT_NAMES:
        return "weapon_name_" + stem
    if r.startswith("scripts/melee/") and name in OFFICIAL_MELEE_SCRIPT_NAMES:
        stem = OFFICIAL_MELEE_NAME_ALIASES.get(stem, stem)
        return "weapon_name_" + stem
    return ""


def pretty_weapon_name(path: Path, kind: str) -> str:
    stem = path.stem
    if stem.lower().startswith("weapon_"):
        stem = stem[7:]
    name = stem.replace("_", " ").replace("-", " ").strip()
    return name.title() if name else path.stem


def parse_numeric_weapon_script(
    path: Path,
    kind: str,
    rel_path: str = "",
    origin: str = "",
    workspace: bool = False,
) -> Optional[WeaponScriptRecord]:
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return None

    lines = text.splitlines(keepends=True)
    entries: list[WeaponValueEntry] = []
    for i, raw in enumerate(lines):
        body = raw.rstrip("\r\n")
        newline = raw[len(body):]
        if body.lstrip().startswith("//"):
            continue
        m = WEAPON_VALUE_RE.match(body)
        if not m:
            continue
        key = m.group("key").strip()
        value = m.group("value").strip()
        entries.append(WeaponValueEntry(
            key=key,
            value=value,
            original=value,
            line_no=i,
            prefix=m.group("prefix"),
            suffix=m.group("suffix"),
            newline=newline,
        ))

    if not entries:
        return None

    rec = WeaponScriptRecord(
        title=pretty_weapon_name(path, kind),
        kind=kind,
        path=str(path),
        rel_path=rel_path or path.name,
        origin=origin,
        workspace=workspace,
        entries=entries,
        lines=lines,
    )
    rec.metrics = simulate_weapon_performance(rec)
    return rec


def _weapon_values(record: WeaponScriptRecord, overrides: Optional[dict[int, str]] = None) -> dict[str, float]:
    values: dict[str, float] = {}
    overrides = overrides or {}
    for entry in record.entries:
        raw = overrides.get(entry.line_no, entry.value)
        try:
            number = float(str(raw).strip())
        except Exception:
            continue
        key = entry.key.lower().replace(" ", "").replace("_", "")
        values[key] = number
    return values


def _pick(values: dict[str, float], names: list[str], default: float) -> float:
    for name in names:
        key = name.lower().replace(" ", "").replace("_", "")
        if key in values:
            return values[key]
    return default


def simulate_weapon_performance(record: WeaponScriptRecord, overrides: Optional[dict[int, str]] = None) -> dict:
    values = _weapon_values(record, overrides)
    is_melee = record.kind == "melee"

    damage_default = 70.0 if is_melee else 20.0
    cycle_default = 0.8 if is_melee else 0.18
    raw_damage = max(0.0, _pick(values, ["damage", "damageperhit"], damage_default))
    bullets = 1.0 if is_melee else max(1.0, _pick(values, ["bullets", "pellets", "pelletcount", "numshots"], 1.0))
    if (not is_melee) and bullets > 1.0 and raw_damage >= 90.0:
        shot_damage = raw_damage
    else:
        shot_damage = raw_damage * bullets
    min_cycle = 0.30 if is_melee else 0.055
    cycle = max(min_cycle, _pick(values, ["cycletime", "refiredelay", "fireinterval", "attackinterval", "swingtime"], cycle_default))
    clip = int(max(1.0, _pick(values, ["clipsize", "clip", "defaultclip", "maxclip"], 1.0 if is_melee else 30.0)))
    reload_time = max(0.0, _pick(values, ["reloadduration", "reloadtime", "reload", "reloademptyduration"], 0.0 if is_melee else 2.35))

    theoretical_dps = shot_damage / cycle
    if not is_melee:
        theoretical_dps = min(theoretical_dps, 5000.0)
    if is_melee:
        sustained_dps = theoretical_dps
        burst_1s = shot_damage * max(1, int(1.0 / cycle))
    else:
        fire_window = clip * cycle
        sustained_dps = (shot_damage * clip) / max(0.05, fire_window + reload_time)
        burst_1s = shot_damage * min(clip, max(1, int(1.0 / cycle)))

    sustained_dps = min(sustained_dps, 5000.0)
    burst_1s = min(burst_1s, 8000.0)

    spread = _pick(values, ["spreadpershot", "maxspread", "minstandingspread", "minduckingspread"], 0.0)
    recoil = _pick(values, ["verticalpunch", "punchangle", "recoil", "maxmovementspread"], 0.0)
    range_mod = _pick(values, ["rangemodifier", "range", "swingrange"], 1.0 if not is_melee else 70.0)

    if is_melee:
        reach_factor = max(0.65, min(1.45, range_mod / 70.0))
        accuracy_factor = reach_factor
    else:
        accuracy_penalty = max(0.0, spread) * 0.18 + max(0.0, recoil) * 0.025
        accuracy_factor = max(0.35, min(1.35, range_mod / 1.0)) / (1.0 + accuracy_penalty)

    score = sustained_dps * accuracy_factor + burst_1s * 0.08 + shot_damage * 0.18
    if not is_melee:
        score += min(clip, 100) * 0.25

    return {
        "damage": shot_damage,
        "cycle": cycle,
        "clip": clip,
        "reload": reload_time,
        "theoretical_dps": theoretical_dps,
        "sustained_dps": sustained_dps,
        "burst_1s": burst_1s,
        "accuracy_factor": accuracy_factor,
        "score": score,
    }


def format_weapon_number(value: float) -> str:
    try:
        if abs(value - round(value)) < 0.005:
            return str(int(round(value)))
        return f"{value:.1f}"
    except Exception:
        return "-"




class SmoothWheelMixin:
    def _smooth_wheel_scroll(self, event):
        try:
            delta_y = event.angleDelta().y()
        except Exception:
            delta_y = 0
        if not delta_y:
            try:
                return super().wheelEvent(event)
            except Exception:
                return
        bar = self.verticalScrollBar()
        if bar is None or bar.maximum() <= bar.minimum():
            try:
                return super().wheelEvent(event)
            except Exception:
                return
        current = bar.value()
        target = getattr(self, "_smooth_scroll_target", current)
        if abs(target - current) > max(160, bar.pageStep() * 2):
            target = current
        base_step = max(48, min(180, int(max(1, bar.pageStep()) * 0.28)))
        target -= int((delta_y / 120.0) * base_step)
        target = max(bar.minimum(), min(bar.maximum(), target))
        self._smooth_scroll_target = target
        anim = getattr(self, "_smooth_scroll_anim", None)
        if anim is None:
            anim = QPropertyAnimation(bar, b"value", self)
            anim.setDuration(135)
            anim.setEasingCurve(QEasingCurve.Type.OutCubic)
            self._smooth_scroll_anim = anim
        anim.stop()
        anim.setStartValue(current)
        anim.setEndValue(target)
        anim.start()
        event.accept()


class SmoothScrollArea(SmoothWheelMixin, QScrollArea):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.verticalScrollBar().setSingleStep(18)
        self.horizontalScrollBar().setSingleStep(18)

    def wheelEvent(self, event):
        self._smooth_wheel_scroll(event)


class SmoothTableWidget(SmoothWheelMixin, QTableWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setVerticalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)
        self.setHorizontalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)
        self.verticalScrollBar().setSingleStep(18)
        self.horizontalScrollBar().setSingleStep(18)

    def wheelEvent(self, event):
        self._smooth_wheel_scroll(event)


class NumericTableWidgetItem(QTableWidgetItem):
    def __init__(self, text: object, numeric: object = None):
        super().__init__(str(text))
        try:
            self._sort_value = float(numeric if numeric is not None else text)
        except Exception:
            self._sort_value = None

    def __lt__(self, other):
        try:
            a = self._sort_value
            b = getattr(other, "_sort_value", None)
            if a is not None and b is not None:
                return a < b
        except Exception:
            pass
        return super().__lt__(other)


class FlowLayout(QLayout):
    def __init__(self, parent=None, margin=0, hspacing=8, vspacing=8):
        super().__init__(parent)
        self._items = []
        self._hspacing = hspacing
        self._vspacing = vspacing
        self.setContentsMargins(margin, margin, margin, margin)

    def addItem(self, item):
        self._items.append(item)

    def count(self):
        return len(self._items)

    def itemAt(self, index):
        return self._items[index] if 0 <= index < len(self._items) else None

    def takeAt(self, index):
        return self._items.pop(index) if 0 <= index < len(self._items) else None

    def expandingDirections(self):
        return Qt.Orientation(0)

    def hasHeightForWidth(self):
        return True

    def heightForWidth(self, width):
        return self._do_layout(QRect(0, 0, width, 0), True)

    def setGeometry(self, rect):
        super().setGeometry(rect)
        self._do_layout(rect, False)

    def sizeHint(self):
        return self.minimumSize()

    def minimumSize(self):
        size = QSize()
        for item in self._items:
            size = size.expandedTo(item.minimumSize())
        left, top, right, bottom = self.getContentsMargins()
        size += QSize(left + right, top + bottom)
        return size

    def _do_layout(self, rect, test_only):
        left, top, right, bottom = self.getContentsMargins()
        effective = rect.adjusted(left, top, -right, -bottom)
        x = effective.x()
        y = effective.y()
        line_height = 0
        for item in self._items:
            hint = item.sizeHint()
            next_x = x + hint.width() + self._hspacing
            if next_x - self._hspacing > effective.right() and line_height > 0:
                x = effective.x()
                y += line_height + self._vspacing
                next_x = x + hint.width() + self._hspacing
                line_height = 0
            if not test_only:
                item.setGeometry(QRect(QPoint(x, y), hint))
            x = next_x
            line_height = max(line_height, hint.height())
        return y + line_height - rect.y() + bottom

# ---------------------------------------------------------------------------
# 主窗口类，连接界面、配置、扫描、安装和启动逻辑。
# Main window class connecting UI, configuration, scanning, installation, and launch logic.
# ---------------------------------------------------------------------------
class DanyriaWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.base = base_dir()
        self.resource_base = resource_dir()
        self.assets = first_existing_dir("assets")
        self.payload = first_existing_dir("payload")
        self.user_data = app_data_dir()
        self.config = {}
        self.theme_key = "normal"
        self.language_setting = "auto"
        self.last_scan_count = None
        self.last_danyria_count = None
        self.l4d2: Optional[Path] = None
        self.records: list[ModRecord] = []
        self.filtered: list[ModRecord] = []
        self._scan_cache: dict[str, tuple[tuple, Optional[ModRecord]]] = {}
        self._scan_cache_root = ""
        self._runtime_status_cache = None
        self.weapon_records: list[WeaponScriptRecord] = []
        self.weapon_filtered: list[WeaponScriptRecord] = []
        self.normal_window_size = QSize(1720, 980)
        self.minimum_window_size = QSize(1580, 880)
        self.maximized = False
        self._entry_animation_done = False
        self._animations = []
        self._resize_margin = 8
        self._resizing_edges = None
        self._resize_start_pos = None
        self._resize_start_geo = None
        self.cursor_overlay = None
        self.hud_process = None
        self.load_config()

        self.setWindowTitle(f"{APP_NAME} v{APP_VERSION}")
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Window)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.apply_icon()
        self.resize(self.normal_window_size)
        self.setMinimumSize(self.minimum_window_size)
        self.setWindowOpacity(0.0)
        self.build_ui()
        self.setAcceptDrops(True)
        self.setMouseTracking(True)
        self.install_mouse_tracking(self)
        QApplication.instance().installEventFilter(self)
        self.apply_theme(self.theme_key, initial=True)
        QTimer.singleShot(600, lambda: self.ensure_steam_integration(silent=True))
        QTimer.singleShot(900, self.auto_check_runtime_environment)
        QTimer.singleShot(0, self.sync_overlay_geometry)
        if self.l4d2:
            self.path_edit.setText(str(self.l4d2))
        else:
            self.auto_detect_path(force=False)
            if self.l4d2:
                self.path_edit.setText(str(self.l4d2))
        if self.l4d2 and self.l4d2.exists() and (self.l4d2 / "addons").exists():
            self.scan()
        QTimer.singleShot(350, self.restore_hud_from_saved_config)

    def load_config(self):
        try:
            self.config = json.loads(cfg_path().read_text(encoding="utf-8"))
            self.theme_key = self.config.get("theme", "normal")
            self.language_setting = self.config.get("language", "auto")
            p = self.config.get("l4d2_path", "")
            if p:
                self.l4d2 = Path(p)
        except Exception:
            pass

    def save_config(self):
        self.config["theme"] = self.theme_key
        self.config["language"] = self.language_setting
        self.config["l4d2_path"] = str(self.l4d2) if self.l4d2 else ""
        try:
            cfg_path().write_text(json.dumps(self.config, ensure_ascii=False, indent=2), encoding="utf-8")
        except Exception:
            pass

    def icon_path_for_theme(self, key=None, target=False) -> Path:
        key = key or self.theme_key
        t = THEMES[key]
        name = t["target_avatar_file"] if target else t["avatar_file"]
        for p in [self.assets / name, self.assets / "avatar.png"]:
            if p.exists():
                return p
        return self.assets / name

    def title_path_for_theme(self, key=None) -> Path:
        key = key or self.theme_key
        t = THEMES[key]
        for p in [self.assets / t["title_file"], self.assets / "title.png"]:
            if p.exists():
                return p
        return self.assets / t["title_file"]

    def apply_icon(self):
        icon = self.icon_path_for_theme()
        if icon.exists():
            self.setWindowIcon(QIcon(str(icon)))

    def qss(self, t):
        checkmark_url = str((self.assets / "checkbox_check.svg").resolve()).replace("\\", "/")
        window_bg = f"qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 {t['bg']}, stop:0.55 {t['bg2']}, stop:1 {t['brand_glow']})"
        title_bg = f"qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 {t['brand_glow']}, stop:0.50 {t['bg']}, stop:1 {t['bg2']})"
        card_bg = f"qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 {t['panel']}, stop:1 {t['panel2']})"
        input_bg = f"qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 {t['panel2']}, stop:1 {t['chip']})"
        button_bg = t.get('button', t['chip'])
        button_hover_bg = f"qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 {t.get('button_hover_a', t['accent'])}, stop:1 {t.get('button_hover_b', t['accent2'])})"
        accent_bg = f"qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 {t.get('button_hover_a', t['accent'])}, stop:1 {t.get('button_hover_b', t['accent2'])})"
        return f"""
QWidget {{
    background: transparent;
    color: {t['text']};
    font-family: "Microsoft YaHei UI", "Segoe UI";
    font-size: 11px;
}}
QFrame#WindowFrame {{
    background: {window_bg};
    border: 1px solid {t['line']};
    border-radius: 18px;
}}
QFrame#TitleBar {{
    background: {title_bg};
    border-top-left-radius: 18px;
    border-top-right-radius: 18px;
}}
QFrame#PathCard, QFrame#TableCard, QFrame#DetailCard {{
    background: {card_bg};
    border: 1px solid {t['line']};
    border-radius: 16px;
}}
QScrollArea {{
    background: transparent;
    border: 0px;
}}
QScrollArea QWidget {{
    background: transparent;
}}

QScrollBar:vertical {{
    background: transparent;
    width: 12px;
    margin: 6px 2px 6px 2px;
    border: 0px;
}}
QScrollBar::handle:vertical {{
    background: rgba(120, 150, 190, 105);
    min-height: 34px;
    border-radius: 5px;
}}
QScrollBar::handle:vertical:hover {{
    background: {t['accent']};
}}
QScrollBar::handle:vertical:pressed {{
    background: {t['accent2']};
}}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical,
QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
    height: 0px;
    background: transparent;
    border: 0px;
}}
QScrollBar:horizontal {{
    background: transparent;
    height: 12px;
    margin: 2px 6px 2px 6px;
    border: 0px;
}}
QScrollBar::handle:horizontal {{
    background: rgba(120, 150, 190, 105);
    min-width: 34px;
    border-radius: 5px;
}}
QScrollBar::handle:horizontal:hover {{
    background: {t['accent']};
}}
QScrollBar::handle:horizontal:pressed {{
    background: {t['accent2']};
}}
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal,
QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {{
    width: 0px;
    background: transparent;
    border: 0px;
}}
QFrame#CollapsibleHeaderFrame {{
    background: transparent;
    border: none;
}}
QPushButton#CollapsibleHeader {{
    background: transparent;
    border: 0px;
    border-radius: 16px;
    padding: 14px 18px;
    color: {t['text']};
    font-size: 15px;
    font-weight: 800;
    text-align: left;
}}
QPushButton#CollapsibleHeader:hover {{
    background: {input_bg};
}}
QPushButton#CollapsibleHeader:pressed {{
    background: {t['brand_glow']};
}}
QFrame#LeftPlain {{
    background: transparent;
    border: none;
}}
QLabel#SectionTitle {{
    background: transparent;
    border: none;
    color: {t['text']};
    font-size: 17px;
    font-weight: 800;
    padding: 0px;
    margin: 0px;
}}
QLabel#BrandTitle {{
    background: transparent;
    border: none;
    color: {t['brand_title']};
    font-family: "Bahnschrift SemiBold", "Segoe UI Semibold", "Trebuchet MS", "Microsoft YaHei UI";
    font-size: 34px;
    font-weight: 800;
    letter-spacing: 4px;
    padding: 0px;
    margin: 0px;
}}
QLabel#BrandVersion {{
    background: transparent;
    border: none;
    color: {t['brand_version']};
    font-family: "Segoe UI Semibold", "Consolas", "Microsoft YaHei UI";
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 2px;
    padding: 0px;
    margin: 0px;
}}
QLabel#BrandLogo {{
    background: transparent;
    border: none;
    padding: 0px;
    margin: 0px;
}}
QLabel#TinyText, QLabel#Muted {{
    background: transparent;
    border: 0px;
    color: {t['muted']};
}}
QLabel#DropHintBanner {{
    background: {input_bg};
    border: 1px solid {t['accent']};
    border-radius: 12px;
    color: {t['text']};
    font-size: 12px;
    font-weight: 800;
    padding: 9px 12px;
}}
QLineEdit#WeaponPackPathEdit, QLineEdit#WeaponWorkspacePathEdit {{
    font-family: "Consolas", "Microsoft YaHei UI", "Segoe UI";
}}
QLabel#Pill {{
    background: {input_bg};
    color: {t['chip_text']};
    border-radius: 10px;
    padding: 5px 9px;
    font-weight: 700;
    border: 1px solid {t['line']};
}}
QLabel#GroupLabel {{
    background: transparent;
    color: {t['subtle']};
    font-size: 11px;
    font-weight: 900;
    letter-spacing: 1px;
    padding: 9px 4px 2px 4px;
}}
QFrame#ButtonGroup {{
    background: rgba(255, 255, 255, 24);
    border: 1px solid {t['line']};
    border-radius: 14px;
}}
QLineEdit, QComboBox, QTextEdit {{
    background: {input_bg};
    border: 1px solid {t['line']};
    border-radius: 11px;
    padding: 8px 10px;
    selection-background-color: {t['accent']};
    selection-color: {t['text']};
    color: {t['text']};
}}
QComboBox QAbstractItemView {{
    background: {t['panel']};
    color: {t['text']};
    border: 1px solid {t['line']};
    selection-background-color: {t['chip']};
    selection-color: {t['text']};
    outline: 0px;
    padding: 6px;
}}
QComboBox QAbstractItemView::item {{
    min-height: 28px;
    padding: 6px 10px;
}}
QMessageBox, QMessageBox QWidget {{
    background: {t['panel']};
    color: {t['text']};
}}
QMessageBox QLabel {{
    background: transparent;
    color: {t['text']};
    font-size: 12px;
    font-weight: 600;
}}
QMessageBox QPushButton {{
    min-width: 86px;
    min-height: 28px;
}}

QLineEdit#HudParamInput {{
    min-height: 30px;
    max-height: 30px;
    padding: 1px 6px;
    font-size: 13px;
    font-weight: 700;
    qproperty-alignment: AlignCenter;
}}
QPushButton {{
    background: {button_bg};
    color: {t.get('button_text', t['text'])};
    border: 1px solid {t['line']};
    border-radius: 11px;
    padding: 7px 10px;
    font-weight: 700;
}}
QPushButton:hover {{
    background: {button_hover_bg};
    border-color: {t['accent']};
    color: {t.get('accent_text', '#10131A')};
}}
QPushButton:pressed {{
    background: {t['brand_glow']};
    color: {t['text']};
}}
QPushButton[accent="true"] {{
    background: {t['accent']};
    color: {t.get('accent_text', '#10131A')};
    border: 1px solid {t['accent']};
}}
QPushButton[accent="true"]:hover {{
    background: {accent_bg};
    border-color: {t['accent2']};
}}
QPushButton[navActive="true"] {{
    background: {accent_bg};
    color: {t.get('accent_text', '#10131A')};
    border: 0px;
}}
QPushButton#TopLaunchButton {{
    min-width: 200px;
    min-height: 48px;
    border-radius: 18px;
    padding: 10px 22px;
    font-size: 16px;
    font-weight: 900;
}}
QPushButton#TopLaunchButton:hover {{
    background: {accent_bg};
    border: 1px solid rgba(255,255,255,150);
}}
QPushButton[iconOnly="true"] {{
    background: transparent;
    border: 0px;
    padding: 3px;
    border-radius: 9px;
}}
QPushButton[iconOnly="true"]:hover {{
    background: {t['chip']};
}}
QPushButton[windowButton="true"] {{
    background: transparent;
    border: 0px;
    padding: 4px;
    border-radius: 8px;
    font-size: 14px;
}}
QPushButton[drawnIcon="true"] {{
    background: transparent;
    border: 0px;
    padding: 0px;
}}
QPushButton[windowButton="true"]:hover {{
    background: {t['chip']};
}}
QPushButton#CloseButton:hover {{
    background: {t['danger']};
    color: #FFFFFF;
}}
QTableWidget {{
    background: {t['panel']};
    alternate-background-color: {t['bg2']};
    border: 0px;
    gridline-color: {t['line']};
    selection-background-color: {t['chip']};
    selection-color: {t['text']};
}}
QHeaderView::section {{
    background: {input_bg};
    color: {t['muted']};
    border: 0px;
    border-right: 1px solid {t['line']};
    border-bottom: 1px solid {t['line']};
    padding: 8px;
    font-weight: 800;
}}
QTableWidget::item {{
    padding: 7px 8px;
    border-right: 1px solid rgba(255, 255, 255, 24);
    border-bottom: 1px solid {t['line']};
}}
QTableWidget#ModTable {{
    gridline-color: transparent;
}}
QTableWidget#ModTable::item {{
    border-right: 0px;
    border-bottom: 0px;
}}
QComboBox::drop-down {{ border: 0px; width: 24px; }}
QSplitter::handle {{ background: transparent; width: 10px; }}
QCheckBox {{
    spacing: 10px;
    padding: 4px 2px;
}}
QCheckBox::indicator {{
    width: 20px;
    height: 20px;
    border-radius: 6px;
    border: 2px solid {t['accent']};
    background: {t['panel2']};
}}
QCheckBox::indicator:hover {{
    border: 2px solid {t['accent2']};
    background: {t['chip']};
}}
QCheckBox::indicator:checked {{
    background: {t['accent']};
    border: 2px solid {t['accent']};
    image: url("{checkmark_url}");
}}
QCheckBox::indicator:checked:hover {{
    background: {t['accent2']};
    border: 2px solid {t['accent2']};
    image: url("{checkmark_url}");
}}
QCheckBox::indicator:disabled {{
    border: 2px solid {t['subtle']};
    background: {t['panel2']};
}}
"""

    def build_ui(self):
        outer = QWidget()
        outer_l = QVBoxLayout(outer)
        outer_l.setContentsMargins(0, 0, 0, 0)
        outer_l.setSpacing(0)
        self.setCentralWidget(outer)

        self.window_frame = QFrame(objectName="WindowFrame")
        outer_l.addWidget(self.window_frame)
        root_l = QVBoxLayout(self.window_frame)
        root_l.setContentsMargins(0, 0, 0, 0)
        root_l.setSpacing(0)

        self.titlebar = TitleBar(self)
        self.titlebar.setFixedHeight(88)
        tb = QHBoxLayout(self.titlebar)
        tb.setContentsMargins(12, 4, 12, 4)
        tb.setSpacing(6)

        self.brand = QWidget()
        self.brand_l = QHBoxLayout(self.brand)
        self.brand_l.setContentsMargins(0, 0, 0, 0)
        self.brand_l.setSpacing(0)

        self.avatar = ImageLabel(80, 80, "")
        self.avatar.setFixedSize(80, 80)
        self.brand_l.addWidget(self.avatar, 0, Qt.AlignmentFlag.AlignVCenter)

        self.brand_logo = BrandLogoWidget()
        self.brand_l.addWidget(self.brand_logo, 1, Qt.AlignmentFlag.AlignVCenter)
        tb.addWidget(self.brand, 0)
        tb.addStretch(1)

        self.status_box = QWidget()
        self.status_l = QVBoxLayout(self.status_box)
        self.status_l.setContentsMargins(0, 0, 0, 0)
        self.status_l.setSpacing(3)

        self.scan_chip = QLabel(self.t("not_scanned"))
        self.scan_chip.setObjectName("Pill")
        self.status_l.addWidget(self.scan_chip)

        self.danyria_chip = QLabel(self.t("danyria_unknown"))
        self.danyria_chip.setObjectName("Pill")
        self.status_l.addWidget(self.danyria_chip)
        tb.addWidget(self.status_box, 0, Qt.AlignmentFlag.AlignVCenter)

        self.top_launch_btn = QPushButton(self.t("launch_l4d2"))
        self.top_launch_btn.setProperty("accent", True)
        self.top_launch_btn.setObjectName("TopLaunchButton")
        self.top_launch_btn.setMinimumSize(200, 48)
        self.top_launch_btn.setFixedHeight(48)
        self.top_launch_btn.clicked.connect(self.launch_game)
        tb.addWidget(self.top_launch_btn, 0, Qt.AlignmentFlag.AlignVCenter)

        self.settings_btn = DrawnIconButton("settings")
        self.settings_btn.setProperty("iconOnly", True)
        self.settings_btn.setFixedSize(36, 36)
        self.settings_btn.setToolTip(self.t("settings"))
        self.settings_btn.clicked.connect(self.open_settings)
        tb.addWidget(self.settings_btn)

        self.min_btn = DrawnIconButton("minimize")
        self.min_btn.setProperty("windowButton", True)
        self.min_btn.setFixedSize(32, 30)
        self.min_btn.clicked.connect(self.showMinimized)
        tb.addWidget(self.min_btn)

        self.max_btn = DrawnIconButton("maximize")
        self.max_btn.setProperty("windowButton", True)
        self.max_btn.setFixedSize(32, 30)
        self.max_btn.clicked.connect(self.toggle_maximize)
        tb.addWidget(self.max_btn)

        self.close_btn = DrawnIconButton("close")
        self.close_btn.setObjectName("CloseButton")
        self.close_btn.setProperty("windowButton", True)
        self.close_btn.setFixedSize(32, 30)
        self.close_btn.clicked.connect(self.close)
        tb.addWidget(self.close_btn)

        root_l.addWidget(self.titlebar)

        content = QWidget()
        content_l = QVBoxLayout(content)
        content_l.setContentsMargins(18, 1, 18, 14)
        content_l.setSpacing(5)
        root_l.addWidget(content, 1)

        self.path_card = QFrame(objectName="PathCard")
        path_card = self.path_card
        p = QVBoxLayout(path_card)
        p.setContentsMargins(12, 6, 12, 6)
        p.setSpacing(6)
        path_row = QHBoxLayout()
        path_row.setSpacing(8)
        self.path_label = QLabel(self.t("path"))
        path_row.addWidget(self.path_label)
        self.path_edit = QLineEdit()
        self.path_edit.setPlaceholderText(r"...\Left 4 Dead 2\left4dead2")
        path_row.addWidget(self.path_edit, 1)
        self.choose_path_btn = self.button(self.t("choose"), self.choose_path)
        self.auto_detect_btn = self.button(self.t("auto_detect"), self.auto_detect_click)
        self.scan_btn = self.button(self.t("scan"), self.scan, accent=True)
        self.open_game_dir_btn = self.button(self.t("open_game_dir"), self.open_game_dir)
        for _path_btn in (self.choose_path_btn, self.auto_detect_btn, self.scan_btn, self.open_game_dir_btn):
            _path_btn.setMinimumWidth(86)
            _path_btn.setMaximumWidth(140)
            path_row.addWidget(_path_btn, 0)
        p.addLayout(path_row)
        content_l.addWidget(path_card)

        self.page_nav = QHBoxLayout()
        self.page_nav.setSpacing(8)
        self.plugins_page_btn = self.button(self.t("page_plugins"), lambda: self.switch_main_page("plugins"))
        self.mods_page_btn = self.button(self.t("page_mods"), lambda: self.switch_main_page("mods"))
        self.weapons_page_btn = self.button(self.t("page_weapons"), lambda: self.switch_main_page("weapons"))
        for _nav_btn in (self.plugins_page_btn, self.mods_page_btn, self.weapons_page_btn):
            _nav_btn.setProperty("navButton", True)
        self.page_nav.addWidget(self.plugins_page_btn)
        self.page_nav.addWidget(self.mods_page_btn)
        self.page_nav.addWidget(self.weapons_page_btn)
        self.page_nav.addStretch(1)
        content_l.addLayout(self.page_nav)

        self.main_stack = QStackedWidget()
        content_l.addWidget(self.main_stack, 1)

        self.plugins_page = QWidget()
        self.plugins_page_l = QVBoxLayout(self.plugins_page)
        self.plugins_page_l.setContentsMargins(0, 0, 0, 0)
        self.plugins_page_l.setSpacing(0)

        self.plugins_scroll = SmoothScrollArea()
        self.plugins_scroll.setWidgetResizable(True)
        self.plugins_scroll.setFrameShape(QFrame.Shape.NoFrame)
        self.plugins_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.plugins_scroll_content = QWidget()
        self.plugins_scroll_l = QVBoxLayout(self.plugins_scroll_content)
        self.plugins_scroll_l.setContentsMargins(0, 0, 6, 0)
        self.plugins_scroll_l.setSpacing(12)
        self.plugins_scroll.setWidget(self.plugins_scroll_content)
        self.plugins_page_l.addWidget(self.plugins_scroll, 1)

        self.plugin_card = CollapsibleSection(self.t("plugin_hud_title"), self.t("plugin_hud_subtitle"), expanded=True)
        plugin_l = self.plugin_card.body_l
        self.plugin_title = QLabel(self.t("plugin_hud_title"))
        self.plugin_title.setObjectName("SectionTitle")
        self.plugin_title.setVisible(False)
        self.plugin_subtitle = QLabel(self.t("plugin_hud_subtitle"))
        self.plugin_subtitle.setObjectName("Muted")
        self.plugin_subtitle.setWordWrap(True)
        self.plugin_subtitle.setVisible(False)

        cards = QHBoxLayout()
        cards.setSpacing(12)

        self.speed_card = QFrame(objectName="PathCard")
        speed_l = QVBoxLayout(self.speed_card)
        speed_l.setContentsMargins(14, 12, 14, 12)
        self.speed_title = QLabel(self.t("speedometer"))
        self.speed_title.setObjectName("SectionTitle")
        self.speed_desc = QLabel(self.t("speedometer_desc"))
        self.speed_desc.setObjectName("Muted")
        self.speed_desc.setWordWrap(True)
        speed_l.addWidget(self.speed_title)
        speed_l.addWidget(self.speed_desc)
        self.speed_enable_check = QCheckBox(self.t("hud_enable_speed"))
        self.speed_enable_check.toggled.connect(lambda checked: self.quick_set_hud_enabled("speed", checked))
        speed_l.addWidget(self.speed_enable_check)
        cards.addWidget(self.speed_card, 1)

        self.enemy_card = QFrame(objectName="PathCard")
        enemy_l = QVBoxLayout(self.enemy_card)
        enemy_l.setContentsMargins(14, 12, 14, 12)
        self.enemy_title = QLabel(self.t("enemy_health"))
        self.enemy_title.setObjectName("SectionTitle")
        self.enemy_desc = QLabel(self.t("enemy_health_desc"))
        self.enemy_desc.setObjectName("Muted")
        self.enemy_desc.setWordWrap(True)
        enemy_l.addWidget(self.enemy_title)
        enemy_l.addWidget(self.enemy_desc)
        self.enemy_enable_check = QCheckBox(self.t("hud_enable_enemy"))
        self.enemy_enable_check.toggled.connect(lambda checked: self.quick_set_hud_enabled("enemy", checked))
        enemy_l.addWidget(self.enemy_enable_check)
        cards.addWidget(self.enemy_card, 1)

        plugin_l.addLayout(cards)

        # 多人/第三方模式开关（开启时弹风险确认；无任何运作说明文本）。
        self.mem_enable_check_hud = QCheckBox(self.mem_tr("enable"))
        self.mem_enable_check_hud.toggled.connect(self.toggle_memory_mode)
        plugin_l.addWidget(self.mem_enable_check_hud)

        self.hud_settings_title = QLabel(self.t("hud_windows_title"))
        self.hud_settings_title.setObjectName("SectionTitle")
        plugin_l.addWidget(self.hud_settings_title)

        self.hud_settings_hint = QLabel(self.t("hud_settings_hint"))
        self.hud_settings_hint.setObjectName("TinyText")
        self.hud_settings_hint.setWordWrap(True)
        plugin_l.addWidget(self.hud_settings_hint)

        settings_row = QHBoxLayout()
        settings_row.setSpacing(16)

        self.speed_settings_card = QFrame(objectName="PathCard")
        self.speed_settings_card.setMinimumWidth(220)
        sp_l = QVBoxLayout(self.speed_settings_card)
        sp_l.setContentsMargins(14, 12, 14, 12)
        sp_l.setSpacing(8)
        self.speed_settings_title = QLabel(self.t("speed_window"))
        self.speed_settings_title.setObjectName("SectionTitle")
        sp_l.addWidget(self.speed_settings_title)

        sp_grid = QGridLayout()
        sp_grid.setContentsMargins(0, 0, 0, 0)
        sp_grid.setHorizontalSpacing(12)
        sp_grid.setVerticalSpacing(7)
        sp_grid.setColumnStretch(0, 1)
        sp_grid.setColumnMinimumWidth(1, 88)
        sp_l.addLayout(sp_grid)

        self.speed_scale_label, self.speed_scale_edit = self.hud_param_row(sp_grid, 0, self.t("hud_scale"), "1.0")
        self.speed_scale_label.hide(); self.speed_scale_edit.hide()
        self.speed_opacity_label, self.speed_opacity_edit = self.hud_param_row(sp_grid, 1, self.t("hud_opacity"), "0.95")
        self.speed_max_label, self.speed_max_edit = self.hud_param_row(sp_grid, 2, self.t("hud_max_speed"), "420")
        settings_row.addWidget(self.speed_settings_card, 1)

        self.enemy_settings_card = QFrame(objectName="PathCard")
        self.enemy_settings_card.setMinimumWidth(240)
        en_l = QVBoxLayout(self.enemy_settings_card)
        en_l.setContentsMargins(14, 12, 14, 12)
        en_l.setSpacing(8)
        self.enemy_settings_title = QLabel(self.t("enemy_window"))
        self.enemy_settings_title.setObjectName("SectionTitle")
        en_l.addWidget(self.enemy_settings_title)

        en_grid = QGridLayout()
        en_grid.setContentsMargins(0, 0, 0, 0)
        en_grid.setHorizontalSpacing(12)
        en_grid.setVerticalSpacing(7)
        en_grid.setColumnStretch(0, 1)
        en_grid.setColumnMinimumWidth(1, 88)
        en_l.addLayout(en_grid)

        self.enemy_scale_label, self.enemy_scale_edit = self.hud_param_row(en_grid, 0, self.t("hud_scale"), "1.0")
        self.enemy_scale_label.hide(); self.enemy_scale_edit.hide()
        self.enemy_opacity_label, self.enemy_opacity_edit = self.hud_param_row(en_grid, 1, self.t("hud_opacity"), "0.95")
        self.enemy_max_label, self.enemy_max_edit = self.hud_param_row(en_grid, 2, self.t("hud_max_enemies"), "6")
        self.enemy_distance_label, self.enemy_distance_edit = self.hud_param_row(en_grid, 3, self.t("hud_enemy_distance"), "1800")
        settings_row.addWidget(self.enemy_settings_card, 1)

        self.penalty_settings_card = QFrame(objectName="PathCard")
        self.penalty_settings_card.setMinimumWidth(220)
        pe_l = QVBoxLayout(self.penalty_settings_card)
        pe_l.setContentsMargins(14, 12, 14, 12)
        pe_l.setSpacing(8)
        self.penalty_settings_title = QLabel(self.t("penalty_window"))
        self.penalty_settings_title.setObjectName("SectionTitle")
        pe_l.addWidget(self.penalty_settings_title)
        pe_grid = QGridLayout()
        pe_grid.setContentsMargins(0, 0, 0, 0)
        pe_grid.setHorizontalSpacing(12)
        pe_grid.setVerticalSpacing(7)
        pe_grid.setColumnStretch(0, 1)
        pe_grid.setColumnMinimumWidth(1, 88)
        pe_l.addLayout(pe_grid)
        self.penalty_scale_label, self.penalty_scale_edit = self.hud_param_row(pe_grid, 0, self.t("hud_scale"), "1.0")
        self.penalty_scale_label.hide(); self.penalty_scale_edit.hide()
        self.penalty_opacity_label, self.penalty_opacity_edit = self.hud_param_row(pe_grid, 1, self.t("hud_opacity"), "0.95")

        plugin_l.addLayout(settings_row)

        self.hud_transparent_note = QLabel(self.t("hud_transparent_note"))
        self.hud_transparent_note.setObjectName("TinyText")
        self.hud_transparent_note.setWordWrap(True)
        plugin_l.addWidget(self.hud_transparent_note)

        hud_cfg_btns = QHBoxLayout()
        self.save_hud_settings_btn = self.button(self.t("hud_save_settings"), self.save_hud_settings, accent=True)
        self.reset_hud_settings_btn = self.button(self.t("hud_reset_settings"), self.reset_hud_settings)
        hud_cfg_btns.addWidget(self.save_hud_settings_btn)
        hud_cfg_btns.addWidget(self.reset_hud_settings_btn)
        hud_cfg_btns.addStretch(1)
        plugin_l.addLayout(hud_cfg_btns)

        self.hud_plugin_status_label = self.plugin_card.status_badge
        self.hud_plugin_status_label.setObjectName("Pill")

        self.hud_plugin_desc = QLabel(self.t("hud_plugin_desc"))
        self.hud_plugin_desc.setObjectName("Muted")
        self.hud_plugin_desc.setWordWrap(True)
        plugin_l.addWidget(self.hud_plugin_desc)

        self.hud_launch_hint = QLabel(self.t("hud_launch_hint"))
        self.hud_launch_hint.setObjectName("TinyText")
        self.hud_launch_hint.setWordWrap(True)
        self.hud_launch_hint.setVisible(bool(self.t("hud_launch_hint").strip()))
        plugin_l.addWidget(self.hud_launch_hint)

        plugin_btns = QHBoxLayout()
        self.install_hud_plugin_btn = self.button(self.t("install_hud_plugin"), self.install_hud_plugin, accent=True)
        self.delete_hud_plugin_btn = self.button(self.t("delete_hud_plugin"), self.delete_hud_plugin)
        self.open_telemetry_btn = self.button(self.t("open_telemetry_folder"), self.open_ems)
        plugin_btns.addWidget(self.install_hud_plugin_btn)
        plugin_btns.addWidget(self.delete_hud_plugin_btn)
        plugin_btns.addWidget(self.open_telemetry_btn)
        plugin_btns.addStretch(1)
        plugin_l.addLayout(plugin_btns)

        self.penalty_card = CollapsibleSection(self.t("plugin_penalty_title"), self.t("plugin_penalty_subtitle"), expanded=False)
        penalty_l = self.penalty_card.body_l
        self.penalty_feature_card = QFrame(objectName="PathCard")
        pf_l = QVBoxLayout(self.penalty_feature_card)
        pf_l.setContentsMargins(14, 12, 14, 12)
        self.penalty_feature_title = QLabel(self.t("penalty_mechanism"))
        self.penalty_feature_title.setObjectName("SectionTitle")
        self.penalty_feature_desc = QLabel(self.t("penalty_mechanism_desc"))
        self.penalty_feature_desc.setObjectName("Muted")
        self.penalty_feature_desc.setWordWrap(True)
        pf_l.addWidget(self.penalty_feature_title)
        pf_l.addWidget(self.penalty_feature_desc)
        self.score_reference_title = QLabel(self.t("score_reference_title"))
        self.score_reference_title.setObjectName("SectionTitle")
        self.score_reference_desc = QLabel(self.t("score_reference_text"))
        self.score_reference_desc.setObjectName("TinyText")
        self.score_reference_desc.setWordWrap(True)
        pf_l.addSpacing(6)
        pf_l.addWidget(self.score_reference_title)
        pf_l.addWidget(self.score_reference_desc)
        self.penalty_enable_check = QCheckBox(self.t("hud_enable_penalty"))
        self.penalty_enable_check.toggled.connect(lambda checked: self.quick_set_hud_enabled("penalty", checked))
        pf_l.addWidget(self.penalty_enable_check)

        self.score_custom_card = QFrame(objectName="PathCard")
        sc_l = QVBoxLayout(self.score_custom_card)
        sc_l.setContentsMargins(14, 12, 14, 12)
        sc_l.setSpacing(8)
        self.score_custom_title = QLabel(self.t("score_custom_title"))
        self.score_custom_title.setObjectName("SectionTitle")
        self.score_custom_hint = QLabel(self.t("score_custom_hint"))
        self.score_custom_hint.setObjectName("TinyText")
        self.score_custom_hint.setWordWrap(True)
        sc_l.addWidget(self.score_custom_title)
        sc_l.addWidget(self.score_custom_hint)
        sc_grid = QGridLayout()
        sc_grid.setContentsMargins(0, 0, 0, 0)
        sc_grid.setHorizontalSpacing(12)
        sc_grid.setVerticalSpacing(7)
        sc_grid.setColumnStretch(0, 1)
        sc_grid.setColumnStretch(2, 1)
        self.score_rule_edits = {}
        score_rule_order = [
            ("common", "score_rule_common"), ("special", "score_rule_special"),
            ("witch", "score_rule_witch"), ("tank", "score_rule_tank"),
            ("damage_done_score", "score_rule_damage_done_score"), ("damage_done_step", "score_rule_damage_done_step"),
            ("damage_taken_per10", "score_rule_damage_taken_per10"), ("heal", "score_rule_heal"),
            ("incap", "score_rule_incap"), ("death", "score_rule_death"),
            ("ledge", "score_rule_ledge"), ("revive", "score_rule_revive"),
            ("pills", "score_rule_pills"), ("adrenaline", "score_rule_adrenaline"),
            ("supply_small", "score_rule_supply_small"), ("supply_weapon", "score_rule_supply_weapon"),
        ]
        defaults = self.default_score_rules()
        for i, (key, label_key) in enumerate(score_rule_order):
            label = QLabel(self.t(label_key))
            label.setObjectName("TinyText")
            edit = QLineEdit(f"{defaults[key]:g}")
            edit.setObjectName("HudParamInput")
            edit.setFixedWidth(92)
            edit.setFixedHeight(28)
            edit.setAlignment(Qt.AlignmentFlag.AlignCenter)
            row = i // 2
            col = (i % 2) * 2
            sc_grid.addWidget(label, row, col, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
            sc_grid.addWidget(edit, row, col + 1, Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.score_rule_edits[key] = edit
        sc_l.addLayout(sc_grid)

        self.load_hud_settings_to_ui()
        self.load_score_rules_to_ui()
        penalty_l.addWidget(self.penalty_feature_card)
        penalty_l.addWidget(self.score_custom_card)
        penalty_l.addWidget(self.penalty_settings_card)
        penalty_save_row = QHBoxLayout()
        self.save_penalty_hud_settings_btn = self.button(self.t("score_save_params"), self.save_penalty_score_params, accent=True)
        self.reset_penalty_params_btn = self.button(self.t("score_reset_params"), self.reset_penalty_score_params)
        penalty_save_row.addWidget(self.save_penalty_hud_settings_btn)
        penalty_save_row.addWidget(self.reset_penalty_params_btn)
        penalty_save_row.addStretch(1)
        penalty_l.addLayout(penalty_save_row)

        self.penalty_plugin_status_label = self.penalty_card.status_badge
        self.penalty_plugin_status_label.setObjectName("Pill")
        self.penalty_plugin_desc = QLabel(self.t("penalty_plugin_desc"))
        self.penalty_plugin_desc.setObjectName("Muted")
        self.penalty_plugin_desc.setWordWrap(True)
        penalty_l.addWidget(self.penalty_plugin_desc)
        self.penalty_launch_hint = QLabel(self.t("penalty_launch_hint"))
        self.penalty_launch_hint.setObjectName("TinyText")
        self.penalty_launch_hint.setWordWrap(True)
        self.penalty_launch_hint.setVisible(bool(self.t("penalty_launch_hint").strip()))
        penalty_l.addWidget(self.penalty_launch_hint)

        penalty_btns = QHBoxLayout()
        self.install_penalty_plugin_btn = self.button(self.t("install_penalty_plugin"), self.install_penalty_plugin, accent=True)
        self.delete_penalty_plugin_btn = self.button(self.t("delete_penalty_plugin"), self.delete_penalty_plugin)
        penalty_btns.addWidget(self.install_penalty_plugin_btn)
        penalty_btns.addWidget(self.delete_penalty_plugin_btn)
        penalty_btns.addStretch(1)
        penalty_l.addLayout(penalty_btns)

        self.plugins_scroll_l.addWidget(self.plugin_card)
        self.plugins_scroll_l.addWidget(self.penalty_card)
        self.plugins_scroll_l.addStretch(1)

        self.mods_page = QWidget()
        self.mods_page_l = QVBoxLayout(self.mods_page)
        self.mods_page_l.setContentsMargins(0, 0, 0, 0)
        self.mods_page_l.setSpacing(0)

        self.weapons_page = QWidget()
        self.weapons_page_l = QVBoxLayout(self.weapons_page)
        self.weapons_page_l.setContentsMargins(0, 0, 0, 0)
        self.weapons_page_l.setSpacing(0)
        self.build_weapons_page()

        self.main_stack.addWidget(self.plugins_page)
        self.main_stack.addWidget(self.mods_page)
        self.main_stack.addWidget(self.weapons_page)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setChildrenCollapsible(False)
        splitter.setHandleWidth(18)

        self.left_panel = QFrame(objectName="LeftPlain")
        left = self.left_panel
        left.setMinimumWidth(250)
        left.setMaximumWidth(270)
        left_l = QVBoxLayout(left)
        left_l.setContentsMargins(4, 8, 6, 8)
        left_l.setSpacing(5)

        self.mods_title = QLabel(self.t("mod_manage"))
        self.mods_title.setObjectName("SectionTitle")
        left_l.addSpacing(6)
        left_l.addWidget(self.mods_title)

        self.drop_hint = QLabel(self.t("drop_hint"))
        self.drop_hint.setObjectName("TinyText")
        self.drop_hint.setWordWrap(True)
        left_l.addWidget(self.drop_hint)

        self.open_selected_btn = self.button(self.t("open_selected"), self.open_selected)
        self.toggle_selected_btn = self.button(self.t("toggle_selected"), self.toggle_selected)
        self.select_all_mods_btn = self.button(self.t("select_all_mods"), self.select_all_mods)
        self.open_addons_btn = self.button(self.t("open_addons"), self.open_addons)
        self.open_workshop_btn = self.button(self.t("open_workshop"), self.open_workshop)
        self.sync_workshop_btn = self.button(self.t("sync_workshop"), self.sync_workshop_items, accent=True)
        self.open_workshop_page_btn = self.button(self.t("workshop_open_page_selected"), self.open_selected_workshop_pages)
        self.unsubscribe_workshop_btn = self.button(self.t("unsubscribe_workshop_selected"), self.unsubscribe_selected_workshop_items)
        self.restore_workshop_btn = self.button(self.t("restore_workshop_history"), self.open_workshop_history_dialog)
        self.steam_status_label = QLabel(self.t("steam_status_not_running"))
        self.steam_status_label.setObjectName("TinyText")
        self.steam_status_label.setWordWrap(True)
        self.steam_connect_btn = self.button(self.t("steam_connect"), self.connect_steam_client, accent=True)
        self.mod_selected_hint = QLabel(self.t("mod_selected_workshop_hint"))
        self.mod_selected_hint.setObjectName("TinyText")
        self.mod_selected_hint.setWordWrap(True)
        self.add_button_group(left_l, self.t("mod_group_selected"), [self.open_selected_btn, self.toggle_selected_btn, self.select_all_mods_btn], self.mod_selected_hint)
        self.add_button_group(left_l, self.t("mod_group_local"), [self.open_addons_btn, self.open_workshop_btn])
        self.add_button_group(left_l, self.t("mod_group_workshop"), [self.sync_workshop_btn, self.open_workshop_page_btn, self.unsubscribe_workshop_btn, self.restore_workshop_btn])
        self.add_button_group(left_l, self.t("mod_group_steam"), [self.steam_connect_btn], self.steam_status_label)
        QTimer.singleShot(300, self.update_steam_status_label)
        left_l.addStretch(1)
        splitter.addWidget(left)

        self.table_card = QFrame(objectName="TableCard")
        center = self.table_card
        center_l = QVBoxLayout(center)
        center_l.setContentsMargins(12, 12, 12, 12)
        center_l.setSpacing(10)

        toolbar = QHBoxLayout()
        self.search = QLineEdit()
        self.search.setPlaceholderText(self.t("search_placeholder"))
        self.search.textChanged.connect(self.apply_filter)
        self.cat_filter = QComboBox()
        self.cat_filter.addItem(self.t("filter_all_categories"), "__all__")
        self.cat_filter.currentIndexChanged.connect(self.apply_filter)
        self.source_filter = QComboBox()
        self.source_filter.addItem(self.t("filter_all_sources"), "__all__")
        for src_name in ["Local", "Workshop", "Unknown"]:
            self.source_filter.addItem(self.tr_source(src_name), src_name)
        self.source_filter.currentIndexChanged.connect(self.apply_filter)
        self.status_filter = QComboBox()
        self.status_filter.addItem(self.t("filter_all_status"), "__all__")
        for st in ["Enabled", "Disabled", "Subscribed", "Missing", "Broken"]:
            self.status_filter.addItem(self.tr_status(st), st)
        self.status_filter.currentIndexChanged.connect(self.apply_filter)
        toolbar.addWidget(self.search, 1)
        toolbar.addWidget(self.cat_filter)
        toolbar.addWidget(self.source_filter)
        toolbar.addWidget(self.status_filter)
        center_l.addLayout(toolbar)

        self.table = SmoothTableWidget(0, 7)
        self.table.setObjectName("ModTable")
        self.table.setHorizontalHeaderLabels([
            self.t("col_name"), self.t("col_category"), self.t("col_status"),
            self.t("col_type"), self.t("col_source"), self.t("col_size"), self.t("col_id_evidence")
        ])
        self.table.setAlternatingRowColors(True)
        self.table.setShowGrid(False)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setSortingEnabled(True)
        self.table.verticalHeader().setVisible(False)
        self.table.verticalHeader().setDefaultSectionSize(48)
        self.make_columns_resizable(self.table, [360, 120, 160, 92, 130, 92, 460])
        self.table.itemSelectionChanged.connect(self.update_details)
        center_l.addWidget(self.table, 1)
        splitter.addWidget(center)

        self.detail_card = QFrame(objectName="DetailCard")
        right = self.detail_card
        r = QVBoxLayout(right)
        r.setContentsMargins(14, 14, 14, 14)
        self.details_title = QLabel(self.t("details"))
        self.details_title.setObjectName("SectionTitle")
        r.addWidget(self.details_title)
        self.details = QTextEdit()
        self.details.setReadOnly(True)
        r.addWidget(self.details, 1)
        splitter.addWidget(right)

        splitter.setSizes([540, 820, 360])
        self.lock_splitter(splitter)
        self.mods_page_l.addWidget(splitter, 1)

        self.grip = None

        self.cursor_overlay = CursorFxOverlay(self)
        self.sync_overlay_geometry()
        self.switch_main_page("plugins")
        self.update_hud_plugin_status()
        if hasattr(self, "update_penalty_plugin_status"):
            self.update_penalty_plugin_status()

    def detect_language_by_timezone(self) -> str:
        candidates = []
        try:
            candidates.append(locale.getlocale()[0])
        except Exception:
            pass
        try:
            candidates.append(locale.getdefaultlocale()[0])
        except Exception:
            pass
        for env_name in ("LANGUAGE", "LC_ALL", "LC_MESSAGES", "LANG"):
            value = os.environ.get(env_name)
            if value:
                candidates.append(value)
        for value in candidates:
            if not value:
                continue
            code = str(value).split(".", 1)[0].replace("-", "_").lower()
            if code.startswith("zh"):
                return "zh" if "zh" in I18N else "en"
            short = code.split("_", 1)[0]
            if short in I18N:
                return short
        return "en"

    def current_language(self) -> str:
        lang = getattr(self, "language_setting", "auto")
        if lang == "auto":
            return self.detect_language_by_timezone()
        return lang if lang in I18N else "en"

    def t(self, key: str, **kwargs) -> str:
        lang = self.current_language()
        text = I18N.get(lang, {}).get(key, I18N.get("en", {}).get(key, I18N[I18N_BASE].get(key, key)))
        try:
            return text.format(**kwargs)
        except Exception:
            return text

    def tv(self, prefix: str, value: str) -> str:
        return self.t(prefix + str(value), **{}) if (prefix + str(value)) in I18N.get(self.current_language(), {}) else str(value)

    def tr_category(self, value: str) -> str:
        return I18N.get(self.current_language(), {}).get("category_" + str(value), I18N[I18N_BASE].get("category_" + str(value), str(value)))

    def tr_status(self, value: str) -> str:
        return I18N.get(self.current_language(), {}).get("status_" + str(value), I18N[I18N_BASE].get("status_" + str(value), str(value)))

    def tr_kind(self, value: str) -> str:
        return I18N.get(self.current_language(), {}).get("kind_" + str(value), I18N[I18N_BASE].get("kind_" + str(value), str(value)))

    def tr_source(self, value: str) -> str:
        return I18N.get(self.current_language(), {}).get("source_" + str(value), I18N[I18N_BASE].get("source_" + str(value), str(value)))

    def update_status_text(self):
        if not hasattr(self, "scan_chip"):
            return

        if self.last_scan_count is None:
            self.scan_chip.setText(self.t("not_scanned"))
        else:
            self.scan_chip.setText(self.t("scanned", n=self.last_scan_count))

        if self.last_danyria_count is None:
            self.danyria_chip.setText(self.t("danyria_unknown"))
        elif self.last_danyria_count:
            self.danyria_chip.setText(self.t("danyria_found", n=self.last_danyria_count))
        else:
            self.danyria_chip.setText(self.t("danyria_none"))

    def update_language(self):
        if not hasattr(self, "path_label"):
            return

        self.setWindowTitle(f"{APP_NAME} v{APP_VERSION}")
        if hasattr(self, "brand_logo"):
            self.brand_logo.set_version(APP_VERSION, self.t("version_label"))
        self.path_label.setText(self.t("path"))
        self.choose_path_btn.setText(self.t("choose"))
        self.auto_detect_btn.setText(self.t("auto_detect"))
        self.scan_btn.setText(self.t("scan"))
        if hasattr(self, "open_game_dir_btn"):
            self.open_game_dir_btn.setText(self.t("open_game_dir"))

        self.top_launch_btn.setText(self.t("launch_l4d2"))
        self.settings_btn.setToolTip(self.t("settings"))

        if hasattr(self, "plugins_page_btn"):
            self.plugins_page_btn.setText(self.t("page_plugins"))
            self.mods_page_btn.setText(self.t("page_mods"))
            if hasattr(self, "weapons_page_btn"):
                self.weapons_page_btn.setText(self.t("page_weapons"))
            self.plugin_title.setText(self.t("plugin_hud_title"))
            self.plugin_subtitle.setText(self.t("plugin_hud_subtitle"))
            if hasattr(self, "plugin_card") and hasattr(self.plugin_card, "set_title"):
                self.plugin_card.set_title(self.t("plugin_hud_title"), self.t("plugin_hud_subtitle"))
            if hasattr(self, "penalty_card") and hasattr(self.penalty_card, "set_title"):
                self.penalty_card.set_title(self.t("plugin_penalty_title"), self.t("plugin_penalty_subtitle"))
            self.speed_title.setText(self.t("speedometer"))
            self.speed_desc.setText(self.t("speedometer_desc"))
            if hasattr(self, "speed_enable_check"):
                self.speed_enable_check.setText(self.t("hud_enable_speed"))
            self.enemy_title.setText(self.t("enemy_health"))
            self.enemy_desc.setText(self.t("enemy_health_desc"))
            if hasattr(self, "enemy_enable_check"):
                self.enemy_enable_check.setText(self.t("hud_enable_enemy"))
            if hasattr(self, "mem_enable_check_hud"):
                self.mem_enable_check_hud.setText(self.mem_tr("enable"))
            self.hud_plugin_desc.setText(self.t("hud_plugin_desc"))
            self.hud_launch_hint.setText(self.t("hud_launch_hint"))
            self.hud_launch_hint.setVisible(bool(self.t("hud_launch_hint").strip()))

            if hasattr(self, "hud_settings_title"):
                self.hud_settings_title.setText(self.t("hud_windows_title"))
                self.hud_settings_hint.setText(self.t("hud_settings_hint"))
                self.speed_settings_title.setText(self.t("speed_window"))
                self.enemy_settings_title.setText(self.t("enemy_window"))
                if hasattr(self, "penalty_settings_title"):
                    self.penalty_settings_title.setText(self.t("penalty_window"))
                    self.penalty_scale_label.setText(self.t("hud_scale"))
                    self.penalty_opacity_label.setText(self.t("hud_opacity"))
                self.speed_scale_label.setText(self.t("hud_scale"))
                self.speed_opacity_label.setText(self.t("hud_opacity"))
                self.speed_max_label.setText(self.t("hud_max_speed"))
                self.enemy_scale_label.setText(self.t("hud_scale"))
                self.enemy_opacity_label.setText(self.t("hud_opacity"))
                self.enemy_max_label.setText(self.t("hud_max_enemies"))
                if hasattr(self, "enemy_distance_label"):
                    self.enemy_distance_label.setText(self.t("hud_enemy_distance"))
                self.hud_transparent_note.setText(self.t("hud_transparent_note"))
                if hasattr(self, "hud_responsive_note"):
                    self.hud_responsive_note.setText(self.t("hud_responsive_note"))
                self.save_hud_settings_btn.setText(self.t("hud_save_settings"))
                self.reset_hud_settings_btn.setText(self.t("hud_reset_settings"))
            self.install_hud_plugin_btn.setText(self.t("install_hud_plugin"))
            if hasattr(self, "delete_hud_plugin_btn"):
                self.delete_hud_plugin_btn.setText(self.t("delete_hud_plugin"))
            self.open_telemetry_btn.setText(self.t("open_telemetry_folder"))
            if hasattr(self, "penalty_feature_title"):
                self.penalty_feature_title.setText(self.t("penalty_mechanism"))
                self.penalty_feature_desc.setText(self.t("penalty_mechanism_desc"))
                if hasattr(self, "score_reference_title"):
                    self.score_reference_title.setText(self.t("score_reference_title"))
                    self.score_reference_desc.setText(self.t("score_reference_text"))
                if hasattr(self, "penalty_enable_check"):
                    self.penalty_enable_check.setText(self.t("hud_enable_penalty"))
                self.penalty_plugin_desc.setText(self.t("penalty_plugin_desc"))
                self.penalty_launch_hint.setText(self.t("penalty_launch_hint"))
                self.penalty_launch_hint.setVisible(bool(self.t("penalty_launch_hint").strip()))
                if hasattr(self, "save_penalty_hud_settings_btn"):
                    self.save_penalty_hud_settings_btn.setText(self.t("score_save_params"))
                if hasattr(self, "reset_penalty_params_btn"):
                    self.reset_penalty_params_btn.setText(self.t("score_reset_params"))
                self.install_penalty_plugin_btn.setText(self.t("install_penalty_plugin"))
                if hasattr(self, "delete_penalty_plugin_btn"):
                    self.delete_penalty_plugin_btn.setText(self.t("delete_penalty_plugin"))
            self.update_hud_plugin_status()
            if hasattr(self, "update_penalty_plugin_status"):
                self.update_penalty_plugin_status()

        self.mods_title.setText(self.t("mod_manage"))
        self.drop_hint.setText(self.t("drop_hint"))
        self.open_selected_btn.setText(self.t("open_selected"))
        self.toggle_selected_btn.setText(self.t("toggle_selected"))
        if hasattr(self, "mod_selected_hint"):
            self.mod_selected_hint.setText(self.t("mod_selected_workshop_hint"))
        if hasattr(self, "select_all_mods_btn"):
            self.select_all_mods_btn.setText(self.t("select_all_mods"))
        self.open_addons_btn.setText(self.t("open_addons"))
        self.open_workshop_btn.setText(self.t("open_workshop"))
        if hasattr(self, "sync_workshop_btn"):
            self.sync_workshop_btn.setText(self.t("sync_workshop"))
            if hasattr(self, "open_workshop_page_btn"):
                self.open_workshop_page_btn.setText(self.t("workshop_open_page_selected"))
            self.unsubscribe_workshop_btn.setText(self.t("unsubscribe_workshop_selected"))
            self.restore_workshop_btn.setText(self.t("restore_workshop_history"))
            if hasattr(self, "steam_connect_btn"):
                self.steam_connect_btn.setText(self.t("steam_connect"))
                self.update_steam_status_label()
        self.details_title.setText(self.t("details"))
        self.search.setPlaceholderText(self.t("search_placeholder"))

        if hasattr(self, "cat_filter"):
            cat_value = self.cat_filter.currentData()
            self.refresh_filters()
            for i in range(self.cat_filter.count()):
                if self.cat_filter.itemData(i) == cat_value:
                    self.cat_filter.setCurrentIndex(i)
                    break

        if hasattr(self, "source_filter"):
            source_value = self.source_filter.currentData()
            self.source_filter.blockSignals(True)
            self.source_filter.clear()
            self.source_filter.addItem(self.t("filter_all_sources"), "__all__")
            for src_name in ["Local", "Workshop", "Unknown"]:
                self.source_filter.addItem(self.tr_source(src_name), src_name)
            for i in range(self.source_filter.count()):
                if self.source_filter.itemData(i) == source_value:
                    self.source_filter.setCurrentIndex(i)
                    break
            self.source_filter.blockSignals(False)

        if hasattr(self, "status_filter"):
            status_value = self.status_filter.currentData()
            self.status_filter.blockSignals(True)
            self.status_filter.clear()
            self.status_filter.addItem(self.t("filter_all_status"), "__all__")
            for st in ["Enabled", "Disabled", "Subscribed", "Missing", "Broken"]:
                self.status_filter.addItem(self.tr_status(st), st)
            for i in range(self.status_filter.count()):
                if self.status_filter.itemData(i) == status_value:
                    self.status_filter.setCurrentIndex(i)
                    break
            self.status_filter.blockSignals(False)

        if hasattr(self, "table"):
            self.table.setHorizontalHeaderLabels([
                self.t("col_name"), self.t("col_category"), self.t("col_status"),
                self.t("col_type"), self.t("col_source"), self.t("col_size"), self.t("col_id_evidence")
            ])
            self.populate_table()

        self.update_weapon_language()
        self.update_status_text()
        self.sync_hud_language_config()

    def startup_value_name(self) -> str:
        return "Danyria"

    def startup_command(self) -> str:
        import sys
        if getattr(sys, "frozen", False):
            return f'"{sys.executable}"'
        return f'"{sys.executable}" "{Path(__file__).resolve()}"'

    def is_autostart_enabled(self) -> bool:
        if os.name != "nt":
            return False
        try:
            import winreg
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_READ) as key:
                value, _ = winreg.QueryValueEx(key, self.startup_value_name())
            return bool(value)
        except Exception:
            return False

    def set_autostart(self, enabled: bool):
        if os.name != "nt":
            return False
        try:
            import winreg
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_SET_VALUE) as key:
                if enabled:
                    winreg.SetValueEx(key, self.startup_value_name(), 0, winreg.REG_SZ, self.startup_command())
                else:
                    try:
                        winreg.DeleteValue(key, self.startup_value_name())
                    except FileNotFoundError:
                        pass
            return True
        except Exception as exc:
            QMessageBox.warning(self, self.t("settings"), str(exc))
            return False

    def runtime_requirements(self):
        return [
            {"modules": ["PySide6", "PyQt6"], "package": "PySide6", "label": "Qt (PySide6/PyQt6)"},
        ]

    def _subprocess_no_window_flags(self) -> int:
        if os.name == "nt":
            return getattr(subprocess, "CREATE_NO_WINDOW", 0)
        return 0

    def _subprocess_startupinfo(self):
        if os.name != "nt":
            return None
        try:
            si = subprocess.STARTUPINFO()
            si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            si.wShowWindow = 0
            return si
        except Exception:
            return None

    def runtime_python_candidates(self):
        seen = set()
        candidates = []

        def add(cmd):
            key = tuple(cmd)
            if key not in seen:
                seen.add(key)
                candidates.append(list(cmd))

        if not getattr(sys, "frozen", False):
            exe = getattr(sys, "executable", "")
            if exe:
                add([exe])
        add(["py", "-3"])
        add(["python"])
        add(["python3"])
        return candidates

    def hud_python_launch_candidates(self):
        seen = set()
        candidates = []

        def add(cmd):
            key = tuple(cmd)
            if key not in seen:
                seen.add(key)
                candidates.append(list(cmd))

        if not getattr(sys, "frozen", False):
            exe = getattr(sys, "executable", "")
            if exe:
                add([exe])
        add(["pythonw"])
        add(["pyw", "-3"])
        add(["py", "-3"])
        add(["python"])
        add(["python3"])
        return candidates

    def hud_script_candidates(self) -> list[Path]:
        return [
            self.payload / "danyria_hud" / "DanyriaHUD.pyw",
            self.base / "payload" / "danyria_hud" / "DanyriaHUD.pyw",
            self.resource_base / "payload" / "danyria_hud" / "DanyriaHUD.pyw",
            self.payload / "danyria_mod_v0_8_resizable_avatar_left" / "danyria_hud" / "DanyriaHUD.pyw",
        ]

    def hud_script_path(self) -> Optional[Path]:
        for path in self.hud_script_candidates():
            try:
                if path.exists():
                    return path
            except Exception:
                pass
        return None

    def hud_exe_candidates(self) -> list[Path]:
        return [
            self.base / "DanyriaHUD.exe",
            self.base / "payload" / "danyria_hud" / "DanyriaHUD.exe",
            self.payload / "danyria_hud" / "DanyriaHUD.exe",
        ]

    def hud_exe_path(self) -> Optional[Path]:
        for path in self.hud_exe_candidates():
            try:
                if path.exists():
                    return path
            except Exception:
                pass
        return None

    def append_runtime_log(self, text: str):
        try:
            log_dir = app_data_dir() / "logs"
            log_dir.mkdir(parents=True, exist_ok=True)
            with (log_dir / "danyria_runtime.log").open("a", encoding="utf-8", errors="replace") as f:
                f.write(time.strftime("[%Y-%m-%d %H:%M:%S] "))
                f.write(str(text).rstrip() + "\n")
        except Exception:
            pass

    def _run_python_check(self, cmd, code: str, timeout: int = 12):
        try:
            return subprocess.run(
                list(cmd) + ["-c", code],
                capture_output=True,
                text=True,
                timeout=timeout,
                creationflags=self._subprocess_no_window_flags(),
                startupinfo=self._subprocess_startupinfo(),
            )
        except Exception as exc:
            class Result:
                returncode = 1
                stdout = ""
                stderr = str(exc)
            return Result()

    def find_runtime_python(self):
        for cmd in self.runtime_python_candidates():
            res = self._run_python_check(cmd, "import sys; print(sys.executable)")
            if getattr(res, "returncode", 1) == 0:
                exe = (getattr(res, "stdout", "") or "").strip().splitlines()
                return cmd, exe[-1] if exe else " ".join(cmd)
        return None, ""

    def runtime_environment_status(self) -> dict:
        frozen = bool(getattr(sys, "frozen", False))
        if frozen:
            status = {
                "python_cmd": [sys.executable],
                "python": True,
                "python_desc": "bundled runtime",
                "pip": True,
                "modules": {},
                "missing_packages": [],
                "steam_integration": self.ensure_steam_integration(silent=True),
                "hud": self.hud_runtime_status(),
                "frozen": True,
            }
            for req in self.runtime_requirements():
                ok = False
                for module in req.get("modules") or [req.get("module")]:
                    try:
                        __import__(module)
                        ok = True
                        break
                    except Exception:
                        pass
                status["modules"][req["label"]] = ok
                if not ok:
                    status["missing_packages"].append(req["package"])
            return status

        py_cmd, py_desc = self.find_runtime_python()
        status = {
            "python_cmd": py_cmd,
            "python": bool(py_cmd),
            "python_desc": py_desc,
            "pip": False,
            "modules": {},
            "missing_packages": [],
            "steam_integration": self.ensure_steam_integration(silent=True),
            "hud": {"ready": False, "message": "Runtime Python was not found."},
            "frozen": False,
        }
        if not py_cmd:
            return status

        pip_res = self._run_python_check(py_cmd, "import pip; print('ok')")
        status["pip"] = getattr(pip_res, "returncode", 1) == 0
        for req in self.runtime_requirements():
            modules = req.get("modules") or [req.get("module")]
            ok = False
            for module in modules:
                if not module:
                    continue
                res = self._run_python_check(py_cmd, f"import {module}; print('ok')")
                if getattr(res, "returncode", 1) == 0:
                    ok = True
                    break
            status["modules"][req["label"]] = ok
            if not ok:
                status["missing_packages"].append(req["package"])
        status["hud"] = self.hud_runtime_status(py_cmd=py_cmd)
        return status

    def hud_runtime_status(self, py_cmd: Optional[list] = None) -> dict:
        env = os.environ.copy()
        try:
            env["DANYRIA_HUD_CONFIG"] = str(self.hud_config_path())
        except Exception:
            pass
        commands = []
        hud_exe = self.hud_exe_path()
        if hud_exe:
            commands.append([str(hud_exe), "--self-test"])
        if getattr(sys, "frozen", False):
            commands.append([str(sys.executable), "--danyria-hud-self-test"])
        else:
            hud = self.hud_script_path()
            if hud:
                base_cmd = py_cmd or [sys.executable]
                commands.append(list(base_cmd) + [str(hud), "--self-test"])

        if not commands:
            return {"ready": False, "message": "HUD program was not found."}

        last_error = ""
        for cmd in commands:
            try:
                res = subprocess.run(
                    cmd,
                    cwd=str(self.base),
                    env=env,
                    capture_output=True,
                    text=True,
                    timeout=8,
                    creationflags=self._subprocess_no_window_flags(),
                    startupinfo=self._subprocess_startupinfo(),
                )
                out = ((res.stdout or "") + "\n" + (res.stderr or "")).strip()
                if res.returncode == 0:
                    return {"ready": True, "message": "HUD self-test passed.", "command": " ".join(cmd), "output": out}
                last_error = out or f"Exit code {res.returncode}"
            except Exception as exc:
                last_error = str(exc)
        return {"ready": False, "message": last_error or "HUD self-test failed."}

    def format_runtime_status(self, status: Optional[dict] = None) -> str:
        status = status or getattr(self, "_runtime_status_cache", None) or self.runtime_environment_status()
        lines = []
        if status.get("python"):
            lines.append(self.t("runtime_status_python_ok", path=status.get("python_desc", "")))
        else:
            lines.append(self.t("runtime_status_python_missing"))
        lines.append(self.t("runtime_status_pip_ok") if status.get("pip") else self.t("runtime_status_pip_missing"))
        for req in self.runtime_requirements():
            label = req["label"]
            if status.get("modules", {}).get(label):
                lines.append(self.t("runtime_status_module_ok", name=label))
            else:
                lines.append(self.t("runtime_status_module_missing", name=label))
        steam_info = status.get("steam_integration") or self.ensure_steam_integration(silent=True)
        if steam_info.get("ready"):
            lines.append(self.t("runtime_status_steam_bridge_ok"))
        else:
            msg = steam_info.get("message") or self.t("runtime_status_steam_bridge_missing")
            lines.append(self.t("runtime_status_steam_bridge_missing") + " · " + msg)
        hud_info = status.get("hud") or {"ready": False, "message": "HUD not checked."}
        if hud_info.get("ready"):
            lines.append("HUD 子程序：自检通过 / HUD subprocess: self-test passed")
        else:
            lines.append("HUD 子程序：失败 / HUD subprocess: failed · " + str(hud_info.get("message", "")))
        return "\n".join(lines)

    def ensure_steam_bridge_scaffold(self) -> str:
        # 中文：Steam API 运行文件必须放在稳定、可写的目录中；打包版不能写入一次性解包目录。
        # English: Steam API runtime files must live in a stable writable folder; frozen builds must not write into the temporary extraction dir.
        folder = self.user_data / "steam_bridge"
        try:
            folder.mkdir(parents=True, exist_ok=True)
        except Exception:
            folder = self.base / "steam_bridge"
            folder.mkdir(parents=True, exist_ok=True)
        try:
            readme = folder / "README.txt"
            readme.write_text(
                "Danyria Steam integration component.\n"
                "This folder is maintained automatically by Danyria.\n",
                encoding="utf-8"
            )
        except Exception:
            pass
        try:
            # 中文：SteamAPI_Init 依赖 AppID；把文件放在 DLL 工作目录，加载 DLL 前会 chdir 到这里。
            # English: SteamAPI_Init needs an AppID; place it beside the DLL because the loader chdirs here before calling Steam.
            (folder / "steam_appid.txt").write_text(L4D2_APP_ID, encoding="utf-8")
        except Exception:
            pass
        return str(folder)

    def ensure_runtime_environment(self, silent: bool = True, force: bool = False) -> bool:
        try:
            if force:
                self.ensure_steam_integration(silent=True)
            status = self.runtime_environment_status()
            self._runtime_status_cache = status
            if status.get("python") and status.get("pip") and not status.get("missing_packages") and status.get("steam_integration", {}).get("ready") and status.get("hud", {}).get("ready"):
                if not silent and force:
                    QMessageBox.information(self, self.t("runtime_env_title"), self.t("runtime_all_ok"))
                return True

            py_cmd = status.get("python_cmd")
            if not py_cmd:
                if not silent:
                    QMessageBox.warning(self, self.t("runtime_env_title"), self.t("runtime_python_missing_body"))
                return False

            if not status.get("pip"):
                subprocess.run(
                    list(py_cmd) + ["-m", "ensurepip", "--upgrade"],
                    capture_output=True,
                    text=True,
                    timeout=120,
                    creationflags=self._subprocess_no_window_flags(),
                    startupinfo=self._subprocess_startupinfo(),
                )

            missing = sorted(set(status.get("missing_packages", [])))
            if missing:
                subprocess.run(
                    list(py_cmd) + ["-m", "pip", "install", "--upgrade"] + missing,
                    capture_output=True,
                    text=True,
                    timeout=600,
                    creationflags=self._subprocess_no_window_flags(),
                    startupinfo=self._subprocess_startupinfo(),
                )

            self.ensure_steam_integration(silent=True)
            after = self.runtime_environment_status()
            self._runtime_status_cache = after
            ok = bool(after.get("python") and after.get("pip") and not after.get("missing_packages") and after.get("steam_integration", {}).get("ready") and after.get("hud", {}).get("ready"))
            if not silent:
                if ok:
                    QMessageBox.information(self, self.t("runtime_env_title"), self.t("runtime_fix_done") + "\n\n" + self.format_runtime_status(after))
                else:
                    QMessageBox.warning(self, self.t("runtime_env_title"), self.t("runtime_fix_failed") + "\n\n" + self.format_runtime_status(after))
            return ok
        except Exception as exc:
            if not silent:
                QMessageBox.warning(self, self.t("runtime_env_title"), str(exc))
            return False

    def auto_check_runtime_environment(self):
        try:
            self.ensure_steam_integration(silent=True)
            self._runtime_status_cache = self.runtime_environment_status()
        except Exception:
            pass

    def create_themed_dialog(self, title: str, min_width: int = 520, size: Optional[tuple[int, int]] = None):
        class _AnimatedThemedDialog(QDialog):
            def __init__(self, owner):
                super().__init__(owner)
                self._danyria_animations = []
                self._danyria_shown_once = False

            def showEvent(self, event):
                super().showEvent(event)
                if self._danyria_shown_once:
                    try:
                        self.setWindowOpacity(1.0)
                    except Exception:
                        pass
                    return
                self._danyria_shown_once = True
                try:
                    final_pos = self.pos()
                    self.move(final_pos + QPoint(0, 12))
                    pos_anim = QPropertyAnimation(self, b"pos", self)
                    pos_anim.setDuration(180)
                    pos_anim.setStartValue(self.pos())
                    pos_anim.setEndValue(final_pos)
                    pos_anim.setEasingCurve(QEasingCurve(QEasingCurve.Type.OutCubic))
                    opacity_anim = QPropertyAnimation(self, b"windowOpacity", self)
                    opacity_anim.setDuration(160)
                    opacity_anim.setStartValue(0.0)
                    opacity_anim.setEndValue(1.0)
                    opacity_anim.setEasingCurve(QEasingCurve(QEasingCurve.Type.OutCubic))
                    for anim in (pos_anim, opacity_anim):
                        self._danyria_animations.append(anim)
                        anim.finished.connect(lambda a=anim: self._danyria_animations.remove(a) if a in self._danyria_animations else None)
                        anim.start()
                except Exception:
                    try:
                        self.setWindowOpacity(1.0)
                    except Exception:
                        pass

        dlg = _AnimatedThemedDialog(self)
        dlg.setObjectName("ThemedDialog")
        dlg.setWindowTitle(title or APP_NAME)
        dlg.setModal(True)
        dlg.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.FramelessWindowHint)
        dlg.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        dlg.setWindowOpacity(0.0)
        dlg._danyria_animations = []
        dlg._danyria_shown_once = False
        dlg.setMinimumWidth(int(min_width))
        if size:
            try:
                dlg.resize(int(size[0]), int(size[1]))
            except Exception:
                pass

        t = THEMES[self.theme_key]
        title_bg = f"qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 {t['brand_glow']}, stop:0.50 {t['bg']}, stop:1 {t['bg2']})"
        card_bg = f"qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 {t['panel']}, stop:1 {t['panel2']})"
        input_bg = f"qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 {t['panel2']}, stop:1 {t['chip']})"
        dlg.setStyleSheet(self.qss(t) + f'''
QDialog#ThemedDialog {{
    background: transparent;
    color: {t['text']};
}}
QFrame#ThemedDialogFrame {{
    background: {card_bg};
    border: 1px solid {t['line']};
    border-radius: 18px;
}}
QFrame#ThemedDialogTitleBar {{
    background: {title_bg};
    border-top-left-radius: 18px;
    border-top-right-radius: 18px;
}}
QWidget#ThemedDialogContent {{
    background: {t['panel']};
    border-bottom-left-radius: 18px;
    border-bottom-right-radius: 18px;
}}
QLabel#ThemedDialogBrand {{
    background: transparent;
    color: {t['brand_title']};
    font-family: "Bahnschrift SemiBold", "Segoe UI Semibold", "Microsoft YaHei UI";
    font-size: 14px;
    font-weight: 900;
    letter-spacing: 2px;
}}
QLabel#ThemedDialogTitle {{
    background: transparent;
    color: {t['text']};
    font-size: 13px;
    font-weight: 800;
}}
QTableWidget#WeaponPackTable {{
    background: {t['panel']};
    alternate-background-color: {t['panel2']};
    color: {t['text']};
    border: 1px solid {t['line']};
    gridline-color: {t['line']};
}}
QTableWidget#WeaponPackTable::item {{
    color: {t['text']};
    border-right: 1px solid {t['line']};
    border-bottom: 1px solid {t['line']};
}}
QWidget#PackCheckCell {{
    background: transparent;
}}
QFrame#ThemedDialogFrame QLineEdit,
QFrame#ThemedDialogFrame QComboBox,
QFrame#ThemedDialogFrame QTextEdit {{
    background: {input_bg};
    color: {t['text']};
    border: 1px solid {t['line']};
}}
''')

        outer = QVBoxLayout(dlg)
        outer.setContentsMargins(10, 10, 10, 10)
        outer.setSpacing(0)

        frame = QFrame()
        frame.setObjectName("ThemedDialogFrame")
        outer.addWidget(frame)
        frame_l = QVBoxLayout(frame)
        frame_l.setContentsMargins(0, 0, 0, 0)
        frame_l.setSpacing(0)

        titlebar = QFrame()
        titlebar.setObjectName("ThemedDialogTitleBar")
        titlebar.setFixedHeight(48)
        title_l = QHBoxLayout(titlebar)
        title_l.setContentsMargins(18, 8, 12, 8)
        title_l.setSpacing(10)
        brand = QLabel(APP_NAME.upper())
        brand.setObjectName("ThemedDialogBrand")
        title_label = QLabel(title or APP_NAME)
        title_label.setObjectName("ThemedDialogTitle")
        title_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        close_btn = DrawnIconButton("close")
        close_btn.setObjectName("CloseButton")
        close_btn.setProperty("windowButton", True)
        close_btn.setFixedSize(30, 30)
        close_btn.clicked.connect(dlg.reject)
        title_l.addWidget(brand)
        title_l.addWidget(title_label, 1)
        title_l.addWidget(close_btn)
        frame_l.addWidget(titlebar)

        drag_state = {"pos": None}
        def _dlg_mouse_press(event):
            try:
                if event.button() == Qt.MouseButton.LeftButton:
                    drag_state["pos"] = event.globalPosition().toPoint() if hasattr(event, "globalPosition") else event.globalPos()
                    event.accept()
                    return
            except Exception:
                pass
        def _dlg_mouse_move(event):
            try:
                if drag_state.get("pos") is not None and event.buttons() & Qt.MouseButton.LeftButton:
                    pos = event.globalPosition().toPoint() if hasattr(event, "globalPosition") else event.globalPos()
                    dlg.move(dlg.pos() + (pos - drag_state["pos"]))
                    drag_state["pos"] = pos
                    event.accept()
                    return
            except Exception:
                pass
        def _dlg_mouse_release(event):
            drag_state["pos"] = None
        titlebar.mousePressEvent = _dlg_mouse_press
        titlebar.mouseMoveEvent = _dlg_mouse_move
        titlebar.mouseReleaseEvent = _dlg_mouse_release

        content = QWidget()
        content.setObjectName("ThemedDialogContent")
        content_l = QVBoxLayout(content)
        content_l.setContentsMargins(18, 16, 18, 16)
        content_l.setSpacing(12)
        frame_l.addWidget(content, 1)
        return dlg, content_l

    def open_settings(self):
        dlg, root = self.create_themed_dialog(self.t("settings_title"), min_width=520)

        theme_row = QHBoxLayout()
        theme_label = QLabel(self.t("theme"))
        theme_combo = QComboBox()
        theme_combo.addItem(self.t("theme_normal"), "normal")
        theme_combo.addItem(self.t("theme_ruin"), "ruin")
        theme_combo.setCurrentIndex(0 if self.theme_key == "normal" else 1)
        theme_row.addWidget(theme_label)
        theme_row.addWidget(theme_combo, 1)
        root.addLayout(theme_row)

        lang_row = QHBoxLayout()
        lang_label = QLabel(self.t("language"))
        lang_combo = QComboBox()
        for lang_code in LANG_ORDER:
            if lang_code == "auto":
                lang_combo.addItem(self.t("lang_auto"), "auto")
            else:
                lang_combo.addItem(I18N.get(lang_code, {}).get("language_name", lang_code), lang_code)
        for i in range(lang_combo.count()):
            if lang_combo.itemData(i) == self.language_setting:
                lang_combo.setCurrentIndex(i)
                break
        lang_row.addWidget(lang_label)
        lang_row.addWidget(lang_combo, 1)
        root.addLayout(lang_row)

        startup_cb = QCheckBox(self.t("startup"))
        startup_cb.setChecked(self.is_autostart_enabled())
        if os.name != "nt":
            startup_cb.setEnabled(False)
            startup_cb.setText(self.t("startup") + "  ·  " + self.t("startup_unavailable"))
        root.addWidget(startup_cb)

        runtime_card = QFrame(objectName="PathCard")
        runtime_l = QVBoxLayout(runtime_card)
        runtime_l.setContentsMargins(14, 12, 14, 12)
        runtime_l.setSpacing(8)
        runtime_title = QLabel(self.t("runtime_env_title"))
        runtime_title.setObjectName("SectionTitle")
        runtime_desc = QLabel(self.t("runtime_env_desc"))
        runtime_desc.setObjectName("TinyText")
        runtime_desc.setWordWrap(True)
        runtime_status = QLabel(self.format_runtime_status())
        runtime_status.setObjectName("TinyText")
        runtime_status.setWordWrap(True)
        runtime_l.addWidget(runtime_title)
        runtime_l.addWidget(runtime_desc)
        runtime_l.addWidget(runtime_status)
        runtime_btn_row = QHBoxLayout()
        runtime_fix_btn = QPushButton(self.t("runtime_check_fix"))
        runtime_fix_btn.setProperty("accent", True)
        runtime_btn_row.addWidget(runtime_fix_btn)
        runtime_btn_row.addStretch(1)
        runtime_l.addLayout(runtime_btn_row)
        root.addWidget(runtime_card)

        def refresh_runtime_status():
            runtime_status.setText(self.format_runtime_status())

        def check_fix_runtime():
            runtime_status.setText(self.t("runtime_checking"))
            try:
                QApplication.processEvents()
            except Exception:
                pass
            self.ensure_runtime_environment(silent=False, force=True)
            refresh_runtime_status()

        runtime_fix_btn.clicked.connect(check_fix_runtime)

        btn_row = QHBoxLayout()
        btn_row.addStretch(1)
        cancel_btn = QPushButton(self.t("cancel"))
        cancel_btn.setMinimumWidth(96)
        apply_btn = QPushButton(self.t("apply"))
        apply_btn.setMinimumWidth(96)
        apply_btn.setProperty("accent", True)
        btn_row.addWidget(cancel_btn)
        btn_row.addWidget(apply_btn)
        root.addLayout(btn_row)

        cancel_btn.clicked.connect(dlg.reject)

        def apply_settings():
            self.language_setting = lang_combo.currentData()
            new_theme = theme_combo.currentData()
            if os.name == "nt":
                self.set_autostart(startup_cb.isChecked())
            self.save_config()
            self.apply_theme(new_theme)
            self.update_language()
            dlg.accept()

        apply_btn.clicked.connect(apply_settings)
        try:
            dlg.exec()
        except AttributeError:
            dlg.exec_()

    def hud_param_row(self, grid, row: int, label_text: str, default: str):
        label = QLabel(label_text)
        label.setObjectName("TinyText")
        label.setToolTip(label_text)
        label.setMinimumWidth(120)
        label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)

        edit = QLineEdit(default)
        edit.setObjectName("HudParamInput")
        edit.setFixedWidth(108)
        edit.setFixedHeight(30)
        edit.setAlignment(Qt.AlignmentFlag.AlignCenter)
        edit.setTextMargins(2, 0, 2, 0)
        edit.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)

        grid.addWidget(label, row, 0, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        grid.addWidget(edit, row, 1, Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

        return label, edit

    def hud_config_path(self) -> Path:
        if getattr(sys, "frozen", False):
            return app_data_dir() / "danyria_hud" / "danyria_hud_config.json"
        return self.payload / "danyria_hud" / "danyria_hud_config.json"

    def default_score_rules(self) -> dict:
        return {
            "common": 0.1, "special": 1.5, "witch": 3.0, "tank": 5.0,
            "damage_done_score": 0.1, "damage_done_step": 200.0,
            "damage_taken_per10": -1.0,
            "incap": -10.0, "death": -18.0, "ledge": -6.0,
            "revive": 5.0, "heal": -3.0,
            "pills": -1.5, "adrenaline": -1.5,
            "supply_small": -1.0, "supply_weapon": -2.0,
        }

    def score_rules_path(self) -> Path:
        if getattr(sys, "frozen", False):
            return app_data_dir() / "danyria_hud" / "danyria_hud_score_rules.txt"
        return self.payload / "danyria_hud" / "danyria_hud_score_rules.txt"

    def parse_score_rules_text(self, text: str) -> dict:
        rules = self.default_score_rules()
        for part in str(text or "").strip().split("|"):
            if "=" not in part:
                continue
            key, value = part.split("=", 1)
            key = key.strip()
            if not key or key == "DHUD_SCORE_RULES":
                continue
            try:
                rules[key] = float(value.strip())
            except Exception:
                pass
        return rules

    def read_score_rules(self) -> dict:
        rules = self.default_score_rules()
        for p in (self.score_rules_path(),):
            try:
                if p.exists():
                    rules.update(self.parse_score_rules_text(p.read_text(encoding="utf-8")))
            except Exception:
                pass
        return rules

    def serialize_score_rules(self, rules: dict) -> str:
        ordered = list(self.default_score_rules().keys())
        parts = ["DHUD_SCORE_RULES"]
        for key in ordered:
            try:
                value = float(rules.get(key, self.default_score_rules()[key]))
            except Exception:
                value = float(self.default_score_rules()[key])
            parts.append(f"{key}={value:g}")
        return "|".join(parts)

    def write_score_rules(self, rules: dict):
        line = self.serialize_score_rules(rules)
        p = self.score_rules_path()
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(line, encoding="utf-8")
        try:
            root = self.get_l4d2(silent=True)
            if root:
                ems = root / "ems"
                ems.mkdir(parents=True, exist_ok=True)
                (ems / "danyria_hud_score_rules.txt").write_text(line, encoding="utf-8")
        except Exception:
            pass

    def load_score_rules_to_ui(self):
        if not hasattr(self, "score_rule_edits"):
            return
        rules = self.read_score_rules()
        for key, edit in self.score_rule_edits.items():
            try:
                edit.setText(f"{float(rules.get(key, self.default_score_rules()[key])):g}")
            except Exception:
                edit.setText(str(self.default_score_rules()[key]))

    def collect_score_rules_from_ui(self) -> dict:
        rules = self.read_score_rules()
        if not hasattr(self, "score_rule_edits"):
            return rules
        defaults = self.default_score_rules()
        for key, edit in self.score_rule_edits.items():
            try:
                rules[key] = float(edit.text().strip())
            except Exception:
                rules[key] = defaults[key]
        return rules

    def sync_hud_language_config(self):
        try:
            cfg = self.read_hud_config()
            lang = self.current_language()
            if cfg.get("language") != lang:
                cfg["language"] = lang
                self.write_hud_config(cfg)
        except Exception:
            pass

    def default_hud_config(self) -> dict:
        return {
            "language": self.current_language(),
            "speed": {"enabled": False, "x": 80, "y": 90, "w": 320, "h": 230, "opacity": 0.92, "max_speed": 420},
            "enemy": {"enabled": False, "x": 80, "y": 320, "w": 460, "h": 424, "opacity": 0.92, "max_enemies": 6, "max_distance": 1800},
            "penalty": {"enabled": False, "x": 500, "y": 90, "w": 390, "h": 330, "opacity": 0.92},
            # 多人/三方服内存读取桥（只读外部内存）。warned 记录用户是否已确认风险弹窗。
            "memory": {"enabled": False, "warned": False},
        }

    def read_hud_config(self) -> dict:
        cfg = self.default_hud_config()
        try:
            p = self.hud_config_path()
            if p.exists():
                loaded = json.loads(p.read_text(encoding="utf-8"))
                if isinstance(loaded.get("language"), str):
                    cfg["language"] = loaded.get("language")
                for section in ("speed", "enemy", "penalty", "memory"):
                    if isinstance(loaded.get(section), dict):
                        cfg.setdefault(section, {}).update(loaded[section])
        except Exception:
            pass
        return cfg

    def write_hud_config(self, cfg: dict):
        cfg["language"] = self.current_language()
        p = self.hud_config_path()
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(cfg, ensure_ascii=False, indent=2), encoding="utf-8")

    def any_hud_enabled(self, cfg: Optional[dict] = None) -> bool:
        cfg = cfg or self.read_hud_config()
        return any(bool(cfg.get(section, {}).get("enabled", False)) for section in ("speed", "enemy", "penalty"))

    def ensure_hud_process_running(self, show_errors: bool = False):
        proc = getattr(self, "hud_process", None)
        if proc is not None:
            try:
                if proc.poll() is None:
                    return
            except Exception:
                pass
        self.launch_hud(show_errors=show_errors)

    def sync_hud_switches_from_ui(self, cfg: dict) -> dict:
        try:
            pairs = (
                ("speed", "speed_enable_check"),
                ("enemy", "enemy_enable_check"),
                ("penalty", "penalty_enable_check"),
            )
            for section, attr in pairs:
                if hasattr(self, attr):
                    cfg.setdefault(section, {})["enabled"] = bool(getattr(self, attr).isChecked())
        except Exception:
            pass
        return cfg

    def restore_hud_from_saved_config(self):
        try:
            cfg = self.read_hud_config()
            self._loading_hud_ui = True
            try:
                self.load_hud_settings_to_ui()
            finally:
                self._loading_hud_ui = False
            self.write_hud_config(cfg)
            if self.any_hud_enabled(cfg):
                self.ensure_hud_process_running(show_errors=False)
            else:
                self.stop_hud_process()
        except Exception:
            pass

    def quick_set_hud_enabled(self, section: str, enabled: bool):
        if getattr(self, "_loading_hud_ui", False):
            return
        try:
            cfg = self.read_hud_config()
            cfg.setdefault(section, {})["enabled"] = bool(enabled)
            self.write_hud_config(cfg)
            if self.any_hud_enabled(cfg):
                self.ensure_hud_process_running(show_errors=False)
            else:
                self.stop_hud_process()
        except Exception:
            pass

    # 内存桥文案：一处集中、每条一次写齐 8 种语言（比逐条对照的旧 i18n 更省事）。
    # 以后新增 UI 文本，推荐照这个 key -> {lang: text} 的写法，不用再去 8 套字典里挨个加。
    MEM_TEXT = {
        "enable": {
            "zh": "多人/第三方模式",
            "en": "Multiplayer / 3rd-party mode",
            "ja": "マルチ/サードパーティモード",
            "ko": "멀티/서드파티 모드",
            "ru": "Режим мульти/сторонних серверов",
            "de": "Mehrspieler-/Drittanbieter-Modus",
            "fr": "Mode multijoueur / tiers",
            "es": "Modo multijugador / terceros",
        },
        "warn_title": {
            "zh": "多人/第三方模式",
            "en": "Multiplayer / 3rd-party mode",
            "ja": "マルチ/サードパーティモード",
            "ko": "멀티/서드파티 모드",
            "ru": "Режим мульти/сторонних серверов",
            "de": "Mehrspieler-/Drittanbieter-Modus",
            "fr": "Mode multijoueur / tiers",
            "es": "Modo multijugador / terceros",
        },
        "warn_body": {
            "zh": "后果自负，是否开启？",
            "en": "Use at your own risk. Enable?",
            "ja": "自己責任で使用してください。有効にしますか？",
            "ko": "사용에 따른 책임은 본인에게 있습니다. 활성화할까요?",
            "ru": "Используйте на свой риск. Включить?",
            "de": "Nutzung auf eigene Gefahr. Aktivieren?",
            "fr": "Utilisation à vos risques. Activer ?",
            "es": "Úsalo bajo tu responsabilidad. ¿Activar?",
        },
    }

    def mem_tr(self, key: str) -> str:
        entry = self.MEM_TEXT.get(key, {})
        return entry.get(self.current_language()) or entry.get("en") or key

    def _sync_memory_checks(self, checked: bool):
        cb = getattr(self, "mem_enable_check_hud", None)
        if cb is not None:
            cb.blockSignals(True)
            cb.setChecked(bool(checked))
            cb.blockSignals(False)

    def toggle_memory_mode(self, checked: bool):
        if getattr(self, "_loading_hud_ui", False):
            return
        try:
            cfg = self.read_hud_config()
            mem = cfg.setdefault("memory", {})
            if checked:
                # 用本项目自带的 DanyriaMessageBox.question（带 是/否 按钮并返回 StandardButton）；
                # 不能用 .warning（它只有 OK 按钮、永远不返回 Yes，会导致确认后又被取消勾选）。
                resp = QMessageBox.question(self, self.mem_tr("warn_title"), self.mem_tr("warn_body"))
                if resp != QMessageBox.StandardButton.Yes:
                    self._sync_memory_checks(False)
                    return
                mem["enabled"] = True
                mem["warned"] = True
            else:
                mem["enabled"] = False
            self.write_hud_config(cfg)
            self._sync_memory_checks(bool(mem.get("enabled")))
            # 切换数据源需要重启外置 HUD 进程：worker 仅在启动时读取 memory.enabled。
            self.stop_hud_process()
            if self.any_hud_enabled(cfg):
                self.launch_hud(show_errors=False)
        except Exception:
            pass

    def load_hud_settings_to_ui(self):
        if not hasattr(self, "speed_scale_edit"):
            return
        cfg = self.read_hud_config()
        speed = cfg["speed"]
        enemy = cfg["enemy"]
        self._loading_hud_ui = True
        try:
            if hasattr(self, "speed_enable_check"):
                self.speed_enable_check.setChecked(bool(speed.get("enabled", False)))
            if hasattr(self, "enemy_enable_check"):
                self.enemy_enable_check.setChecked(bool(enemy.get("enabled", False)))
            if hasattr(self, "mem_enable_check_hud"):
                self.mem_enable_check_hud.setChecked(bool(cfg.get("memory", {}).get("enabled", False)))
            self.speed_scale_edit.setText(str(speed.get("scale", 1.0)))
            self.speed_opacity_edit.setText(str(speed.get("opacity", 0.92)))
            self.speed_max_edit.setText(str(speed.get("max_speed", 420)))

            self.enemy_scale_edit.setText(str(enemy.get("scale", 1.0)))
            self.enemy_opacity_edit.setText(str(enemy.get("opacity", 0.92)))
            self.enemy_max_edit.setText(str(enemy.get("max_enemies", 6)))
            if hasattr(self, "enemy_distance_edit"):
                self.enemy_distance_edit.setText(str(enemy.get("max_distance", 1800)))
            penalty = cfg.get("penalty", {})
            if hasattr(self, "penalty_enable_check"):
                self.penalty_enable_check.setChecked(bool(penalty.get("enabled", False)))
            if hasattr(self, "penalty_scale_edit"):
                self.penalty_scale_edit.setText(str(penalty.get("scale", 1.0)))
                self.penalty_opacity_edit.setText(str(penalty.get("opacity", 0.92)))
        finally:
            self._loading_hud_ui = False

    def _num(self, edit, default, kind=float, min_value=None, max_value=None):
        try:
            value = kind(edit.text().strip())
        except Exception:
            value = default
        if min_value is not None:
            value = max(min_value, value)
        if max_value is not None:
            value = min(max_value, value)
        return value

    def save_hud_settings(self):
        current = self.read_hud_config()
        cfg = {
            "speed": {
                "x": current.get("speed", {}).get("x", 80),
                "y": current.get("speed", {}).get("y", 90),
                "enabled": self.speed_enable_check.isChecked() if hasattr(self, "speed_enable_check") else current.get("speed", {}).get("enabled", False),
                "w": current.get("speed", {}).get("w", 320),
                "h": current.get("speed", {}).get("h", 230),
                "opacity": self._num(self.speed_opacity_edit, 0.92, float, 0.1, 1.0),
                "max_speed": self._num(self.speed_max_edit, 420, int, 100, 2000),
            },
            "enemy": {
                "x": current.get("enemy", {}).get("x", 80),
                "y": current.get("enemy", {}).get("y", 320),
                "enabled": self.enemy_enable_check.isChecked() if hasattr(self, "enemy_enable_check") else current.get("enemy", {}).get("enabled", False),
                "w": current.get("enemy", {}).get("w", 460),
                "h": current.get("enemy", {}).get("h", 424),
                "opacity": self._num(self.enemy_opacity_edit, 0.92, float, 0.1, 1.0),
                "max_enemies": self._num(self.enemy_max_edit, 6, int, 1, 12),
                "max_distance": self._num(self.enemy_distance_edit, 1800, int, 200, 10000) if hasattr(self, "enemy_distance_edit") else current.get("enemy", {}).get("max_distance", 1800),
            },
            "penalty": {
                "x": current.get("penalty", {}).get("x", 500),
                "y": current.get("penalty", {}).get("y", 90),
                "enabled": self.penalty_enable_check.isChecked() if hasattr(self, "penalty_enable_check") else current.get("penalty", {}).get("enabled", False),
                "w": current.get("penalty", {}).get("w", 390),
                "h": current.get("penalty", {}).get("h", 285),
                "opacity": self._num(self.penalty_opacity_edit, 0.92, float, 0.1, 1.0) if hasattr(self, "penalty_opacity_edit") else current.get("penalty", {}).get("opacity", 0.92),
            },
            # 保留内存桥开关，避免保存 HUD 设置时被清掉。
            "memory": current.get("memory", {"enabled": False, "warned": False}),
        }
        self.write_hud_config(cfg)
        try:
            self.write_score_rules(self.collect_score_rules_from_ui())
        except Exception:
            pass
        self.load_hud_settings_to_ui()
        self.load_score_rules_to_ui()
        if self.any_hud_enabled(cfg):
            self.ensure_hud_process_running(show_errors=False)
        else:
            self.stop_hud_process()
        QMessageBox.information(self, APP_NAME, self.t("hud_settings_saved"))

    def reset_hud_settings(self):
        self.write_hud_config(self.default_hud_config())
        try:
            self.write_score_rules(self.default_score_rules())
        except Exception:
            pass
        self.load_hud_settings_to_ui()
        QMessageBox.information(self, APP_NAME, self.t("hud_settings_reset"))


    def save_penalty_score_params(self):
        current = self.read_hud_config()
        current.setdefault("penalty", {})["enabled"] = self.penalty_enable_check.isChecked() if hasattr(self, "penalty_enable_check") else current.get("penalty", {}).get("enabled", False)
        current.setdefault("penalty", {})["opacity"] = self._num(self.penalty_opacity_edit, 0.92, float, 0.1, 1.0) if hasattr(self, "penalty_opacity_edit") else current.get("penalty", {}).get("opacity", 0.92)
        current.setdefault("penalty", {})["x"] = current.get("penalty", {}).get("x", 500)
        current.setdefault("penalty", {})["y"] = current.get("penalty", {}).get("y", 90)
        current.setdefault("penalty", {})["w"] = current.get("penalty", {}).get("w", 390)
        current.setdefault("penalty", {})["h"] = current.get("penalty", {}).get("h", 330)
        self.write_hud_config(current)
        try:
            self.write_score_rules(self.collect_score_rules_from_ui())
        except Exception:
            pass
        self.load_hud_settings_to_ui()
        self.load_score_rules_to_ui()
        if self.any_hud_enabled(current):
            self.ensure_hud_process_running(show_errors=False)
        else:
            self.stop_hud_process()
        QMessageBox.information(self, APP_NAME, self.t("score_params_saved"))

    def reset_penalty_score_params(self):
        current = self.read_hud_config()
        defaults = self.default_hud_config()
        current["penalty"] = defaults.get("penalty", {}).copy()
        self.write_hud_config(current)
        try:
            self.write_score_rules(self.default_score_rules())
        except Exception:
            pass
        self.load_hud_settings_to_ui()
        self.load_score_rules_to_ui()
        if self.any_hud_enabled(current):
            self.ensure_hud_process_running(show_errors=False)
        else:
            self.stop_hud_process()
        QMessageBox.information(self, APP_NAME, self.t("score_params_reset"))

    def switch_main_page(self, page: str):
        if not hasattr(self, "main_stack"):
            return

        if page == "mods":
            target_widget = self.mods_page
        elif page == "weapons" and hasattr(self, "weapons_page"):
            target_widget = self.weapons_page
        else:
            page = "plugins"
            target_widget = self.plugins_page

        changed = self.main_stack.currentWidget() is not target_widget
        self.main_stack.setCurrentWidget(target_widget)
        if changed:
            self.animate_page_transition(target_widget)
        if page == "weapons" and hasattr(self, "weapons_page") and not self.weapon_records:
            self.scan_weapon_scripts(silent=True)

        pairs = [
            (self.plugins_page_btn, page == "plugins"),
            (self.mods_page_btn, page == "mods"),
        ]
        if hasattr(self, "weapons_page_btn"):
            pairs.append((self.weapons_page_btn, page == "weapons"))
        for b, active in pairs:
            b.setProperty("navActive", active)
            b.style().unpolish(b)
            b.style().polish(b)
            b.update()

    def lock_splitter(self, splitter):
        try:
            splitter.setHandleWidth(10)
            for i in range(1, splitter.count()):
                handle = splitter.handle(i)
                if handle is not None:
                    handle.setEnabled(True)
                    if splitter.orientation() == Qt.Orientation.Horizontal:
                        handle.setCursor(Qt.CursorShape.SplitHCursor)
                        handle.setMinimumWidth(10)
                    else:
                        handle.setCursor(Qt.CursorShape.SplitVCursor)
                        handle.setMinimumHeight(10)
        except Exception:
            pass

    def make_columns_resizable(self, table: QTableWidget, widths: Optional[list[int]] = None):
        try:
            header = table.horizontalHeader()
            header.setSectionsMovable(False)
            header.setStretchLastSection(False)
            header.setMinimumSectionSize(48)
            header.setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
            if widths:
                for col, width in enumerate(widths):
                    if col < table.columnCount():
                        table.setColumnWidth(col, max(48, int(width)))
        except Exception:
            pass

    def build_weapons_page(self):
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setChildrenCollapsible(False)
        splitter.setHandleWidth(18)

        left = QFrame(objectName="TableCard")
        left.setMinimumWidth(390)
        left_l = QVBoxLayout(left)
        left_l.setContentsMargins(12, 12, 12, 12)
        left_l.setSpacing(10)

        self.weapon_panel_title = QLabel(self.t("weapon_panel_title"))
        self.weapon_panel_title.setObjectName("SectionTitle")
        left_l.addWidget(self.weapon_panel_title)

        self.weapon_panel_hint = QLabel(self.t("weapon_panel_hint"))
        self.weapon_panel_hint.setObjectName("TinyText")
        self.weapon_panel_hint.setWordWrap(True)
        left_l.addWidget(self.weapon_panel_hint)

        workspace_row = QHBoxLayout()
        workspace_row.setContentsMargins(0, 0, 0, 0)
        workspace_row.setSpacing(8)
        self.weapon_workspace_label = QLabel(self.t("weapon_workspace_label"))
        self.weapon_workspace_label.setObjectName("TinyText")
        self.weapon_workspace_path_edit = QLineEdit(str(self.weapon_project_dir()))
        self.weapon_workspace_path_edit.setObjectName("WeaponWorkspacePathEdit")
        self.weapon_workspace_path_edit.setReadOnly(True)
        self.weapon_workspace_path_edit.setToolTip(str(self.weapon_project_dir()))
        workspace_row.addWidget(self.weapon_workspace_label)
        workspace_row.addWidget(self.weapon_workspace_path_edit, 1)
        left_l.addLayout(workspace_row)
        self.weapon_drop_extract_hint = QLabel(self.t("weapon_drop_extract_hint"))
        self.weapon_drop_extract_hint.setObjectName("DropHintBanner")
        self.weapon_drop_extract_hint.setWordWrap(True)
        left_l.addWidget(self.weapon_drop_extract_hint)

        weapon_btns = QHBoxLayout()
        weapon_btns.setContentsMargins(0, 0, 0, 0)
        weapon_btns.setSpacing(6)
        self.weapon_scan_btn = self.button(self.t("weapon_scan"), self.scan_weapon_scripts, accent=True)
        self.weapon_unpack_vpk_btn = self.button(self.t("weapon_unpack_vpk"), self.extract_weapon_scripts_from_vpks, accent=True)
        self.weapon_reload_btn = self.button(self.t("weapon_reload"), self.reload_selected_weapon)
        self.weapon_open_scripts_btn = self.button(self.t("weapon_open_scripts"), self.open_scripts_folder)
        for _weapon_btn in (self.weapon_scan_btn, self.weapon_unpack_vpk_btn, self.weapon_reload_btn, self.weapon_open_scripts_btn):
            _weapon_btn.setMinimumWidth(104)
            _weapon_btn.setMaximumWidth(132)
            _weapon_btn.setMinimumHeight(32)
            _weapon_btn.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
            weapon_btns.addWidget(_weapon_btn, 0)
        weapon_btns.addStretch(1)
        left_l.addLayout(weapon_btns)

        self.weapon_search = QLineEdit()
        self.weapon_search.setPlaceholderText(self.t("weapon_search_placeholder"))
        self.weapon_search.textChanged.connect(self.apply_weapon_filter)
        left_l.addWidget(self.weapon_search)

        self.weapon_table = SmoothTableWidget(0, 6)
        self.weapon_table.setHorizontalHeaderLabels([
            self.t("weapon_col_name"), self.t("weapon_col_kind"),
            self.t("weapon_col_dps"), self.t("weapon_col_sustained"), self.t("weapon_col_burst"), self.t("weapon_col_score")
        ])
        self.weapon_table.setAlternatingRowColors(True)
        self.weapon_table.setShowGrid(True)
        self.weapon_table.setGridStyle(Qt.PenStyle.SolidLine)
        self.weapon_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.weapon_table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.weapon_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.weapon_table.setSortingEnabled(True)
        self.weapon_table.verticalHeader().setVisible(False)
        wh = self.weapon_table.horizontalHeader()
        wh.setDefaultAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        self.make_columns_resizable(self.weapon_table, [240, 90, 92, 110, 96, 96])
        self.weapon_table.itemSelectionChanged.connect(self.load_selected_weapon_values)
        left_l.addWidget(self.weapon_table, 1)
        splitter.addWidget(left)

        center = QFrame(objectName="TableCard")
        center.setMinimumWidth(430)
        center_l = QVBoxLayout(center)
        center_l.setContentsMargins(12, 12, 12, 12)
        center_l.setSpacing(10)

        value_header = QHBoxLayout()
        self.weapon_values_title = QLabel(self.t("weapon_values_title"))
        self.weapon_values_title.setObjectName("SectionTitle")
        value_header.addWidget(self.weapon_values_title)
        value_header.addStretch(1)
        center_l.addLayout(value_header)

        value_btns = QHBoxLayout()
        value_btns.setContentsMargins(0, 0, 0, 0)
        value_btns.setSpacing(6)
        self.weapon_save_btn = self.button(self.t("weapon_save"), self.save_selected_weapon, accent=True)
        self.weapon_pack_vpk_btn = self.button(self.t("weapon_pack_vpk"), self.pack_weapon_values_vpk, accent=True)
        self.weapon_open_file_btn = self.button(self.t("weapon_open_file"), self.open_selected_weapon_file)
        self.weapon_open_workspace_btn = self.button(self.t("weapon_open_workspace"), self.open_weapon_workspace)
        for _value_btn in (self.weapon_save_btn, self.weapon_pack_vpk_btn, self.weapon_open_file_btn, self.weapon_open_workspace_btn):
            _value_btn.setMinimumWidth(108)
            _value_btn.setMaximumWidth(144)
            _value_btn.setMinimumHeight(32)
            _value_btn.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
            value_btns.addWidget(_value_btn, 0)
        value_btns.addStretch(1)
        center_l.addLayout(value_btns)

        self.weapon_values_table = SmoothTableWidget(0, 5)
        self.weapon_values_table.setHorizontalHeaderLabels([
            self.t("weapon_param_key"), self.t("weapon_param_label"), self.t("weapon_param_value"),
            self.t("weapon_param_original"), self.t("weapon_param_line")
        ])
        self.weapon_values_table.setAlternatingRowColors(True)
        self.weapon_values_table.setShowGrid(True)
        self.weapon_values_table.setGridStyle(Qt.PenStyle.SolidLine)
        self.weapon_values_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.weapon_values_table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.weapon_values_table.setEditTriggers(
            QAbstractItemView.EditTrigger.DoubleClicked |
            QAbstractItemView.EditTrigger.SelectedClicked |
            QAbstractItemView.EditTrigger.EditKeyPressed
        )
        self.weapon_values_table.verticalHeader().setVisible(False)
        vh = self.weapon_values_table.horizontalHeader()
        vh.setDefaultAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        self.make_columns_resizable(self.weapon_values_table, [160, 210, 120, 120, 80])
        self.weapon_values_table.itemChanged.connect(self.on_weapon_value_changed)
        center_l.addWidget(self.weapon_values_table, 1)
        splitter.addWidget(center)

        right = QFrame(objectName="DetailCard")
        right.setMinimumWidth(390)
        right_l = QVBoxLayout(right)
        right_l.setContentsMargins(14, 14, 14, 14)
        right_l.setSpacing(10)
        self.weapon_perf_title = QLabel(self.t("weapon_perf_title"))
        self.weapon_perf_title.setObjectName("SectionTitle")
        right_l.addWidget(self.weapon_perf_title)
        self.weapon_summary_label = QLabel(self.t("weapon_perf_note"))
        self.weapon_summary_label.setObjectName("TinyText")
        self.weapon_summary_label.setWordWrap(True)
        right_l.addWidget(self.weapon_summary_label)

        self.weapon_info_table = SmoothTableWidget(0, 2)
        self.weapon_info_table.setHorizontalHeaderLabels([self.t("weapon_metric_name"), self.t("weapon_metric_value")])
        self.weapon_info_table.verticalHeader().setVisible(False)
        self.weapon_info_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.weapon_info_table.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
        self.make_columns_resizable(self.weapon_info_table, [160, 180])
        right_l.addWidget(self.weapon_info_table, 1)

        self.weapon_metrics_title = QLabel(self.t("weapon_metrics_title"))
        self.weapon_metrics_title.setObjectName("SectionTitle")
        right_l.addWidget(self.weapon_metrics_title)
        self.weapon_metrics_table = SmoothTableWidget(0, 2)
        self.weapon_metrics_table.setHorizontalHeaderLabels([self.t("weapon_metric_name"), self.t("weapon_metric_value")])
        self.weapon_metrics_table.verticalHeader().setVisible(False)
        self.weapon_metrics_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.weapon_metrics_table.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
        self.make_columns_resizable(self.weapon_metrics_table, [180, 130])
        right_l.addWidget(self.weapon_metrics_table, 2)

        splitter.addWidget(right)

        splitter.setSizes([520, 520, 520])
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 1)
        splitter.setStretchFactor(2, 1)
        self.lock_splitter(splitter)
        self.weapons_page_l.addWidget(splitter, 1)

    def update_weapon_language(self):
        if not hasattr(self, "weapon_table"):
            return
        self.weapon_panel_title.setText(self.t("weapon_panel_title"))
        self.weapon_panel_hint.setText(self.t("weapon_panel_hint"))
        if hasattr(self, "weapon_workspace_label"):
            self.weapon_workspace_label.setText(self.t("weapon_workspace_label"))
        if hasattr(self, "weapon_workspace_path_edit"):
            _workspace = str(self.weapon_project_dir())
            self.weapon_workspace_path_edit.setText(_workspace)
            self.weapon_workspace_path_edit.setToolTip(_workspace)
        if hasattr(self, "weapon_drop_extract_hint"):
            self.weapon_drop_extract_hint.setText(self.t("weapon_drop_extract_hint"))
        self.weapon_scan_btn.setText(self.t("weapon_scan"))
        if hasattr(self, "weapon_unpack_vpk_btn"):
            self.weapon_unpack_vpk_btn.setText(self.t("weapon_unpack_vpk"))
        self.weapon_reload_btn.setText(self.t("weapon_reload"))
        self.weapon_open_scripts_btn.setText(self.t("weapon_open_scripts"))
        self.weapon_search.setPlaceholderText(self.t("weapon_search_placeholder"))
        self.weapon_values_title.setText(self.t("weapon_values_title"))
        self.weapon_perf_title.setText(self.t("weapon_perf_title"))
        if hasattr(self, "weapon_metrics_title"):
            self.weapon_metrics_title.setText(self.t("weapon_metrics_title"))
        self.weapon_save_btn.setText(self.t("weapon_save"))
        if hasattr(self, "weapon_pack_vpk_btn"):
            self.weapon_pack_vpk_btn.setText(self.t("weapon_pack_vpk"))
        self.weapon_open_file_btn.setText(self.t("weapon_open_file"))
        if hasattr(self, "weapon_open_workspace_btn"):
            self.weapon_open_workspace_btn.setText(self.t("weapon_open_workspace"))
        self.weapon_table.setHorizontalHeaderLabels([
            self.t("weapon_col_name"), self.t("weapon_col_kind"),
            self.t("weapon_col_dps"), self.t("weapon_col_sustained"), self.t("weapon_col_burst"), self.t("weapon_col_score")
        ])
        self.weapon_values_table.setHorizontalHeaderLabels([
            self.t("weapon_param_key"), self.t("weapon_param_label"), self.t("weapon_param_value"),
            self.t("weapon_param_original"), self.t("weapon_param_line")
        ])
        if hasattr(self, "weapon_info_table"):
            self.weapon_info_table.setHorizontalHeaderLabels([self.t("weapon_metric_name"), self.t("weapon_metric_value")])
        if hasattr(self, "weapon_metrics_table"):
            self.weapon_metrics_table.setHorizontalHeaderLabels([self.t("weapon_metric_name"), self.t("weapon_metric_value")])
        self.populate_weapon_table()
        self.update_weapon_performance_panel()

    def weapon_project_dir(self) -> Path:
        return self.base / "weapon_values_project"

    def weapon_rel_for_path(self, base: Path, path: Path) -> str:
        try:
            return path.relative_to(base).as_posix().lower()
        except Exception:
            return path.name.lower()

    def weapon_script_paths(self, root: Path) -> list[tuple[Path, str, str, str, bool]]:
        found: dict[str, tuple[Path, str, str, str, bool]] = {}
        source_map = {}
        try:
            source_map = json.loads((self.weapon_project_dir() / "danyria_weapon_sources.json").read_text(encoding="utf-8"))
        except Exception:
            source_map = {}

        def origin_for(rel: str, origin: str, workspace: bool) -> str:
            if workspace and rel in source_map:
                return f"{origin} ← {Path(str(source_map.get(rel))).name}"
            return origin

        def add_from_scripts(scripts_dir: Path, origin: str, workspace: bool):
            if not scripts_dir.exists():
                return
            for child in scripts_dir.iterdir():
                if child.is_file() and child.suffix.lower() == ".txt":
                    rel = self.weapon_rel_for_path(scripts_dir.parent, child)
                    if is_weapon_script_rel(rel):
                        found[rel] = (child, kind_from_weapon_rel(rel), rel, origin_for(rel, origin, workspace), workspace)
            melee = scripts_dir / "melee"
            if melee.exists():
                for child in melee.iterdir():
                    if child.is_file() and child.suffix.lower() == ".txt":
                        rel = self.weapon_rel_for_path(scripts_dir.parent, child)
                        if is_weapon_script_rel(rel):
                            found[rel] = (child, kind_from_weapon_rel(rel), rel, origin_for(rel, origin, workspace), workspace)

        add_from_scripts(root / "scripts", "left4dead2/scripts", False)
        add_from_scripts(self.weapon_project_dir() / "scripts", self.t("weapon_workspace"), True)
        return sorted(found.values(), key=lambda x: (x[1], x[0].stem.lower()))

    def scan_weapon_scripts(self, silent: bool = False):
        root = self.get_l4d2(silent=silent)
        if not root:
            return
        records = []
        for path, kind, rel, origin, workspace in self.weapon_script_paths(root):
            rec = parse_numeric_weapon_script(path, kind, rel, origin, workspace)
            if rec:
                records.append(rec)

        ranked = sorted(records, key=lambda r: r.metrics.get("score", 0), reverse=True)
        for i, rec in enumerate(ranked, 1):
            rec.rank = i

        self.weapon_records = sorted(records, key=lambda r: (r.kind, r.title.lower()))
        self.apply_weapon_filter()
        if not records and not silent:
            QMessageBox.information(self, self.t("weapon_no_scripts_title"), self.t("weapon_no_scripts_body"))
        elif records and not silent and hasattr(self, "weapon_summary_label"):
            self.weapon_summary_label.setText(self.t("weapon_scanned", n=len(records)) + "\n" + self.t("weapon_perf_note"))

    def apply_weapon_filter(self):
        if not hasattr(self, "weapon_search"):
            return
        q = self.weapon_search.text().strip().lower()
        self.weapon_filtered = []
        for rec in self.weapon_records:
            param_text = " ".join(e.key + " " + self.weapon_param_label_text(e.key) for e in rec.entries)
            hay = " ".join([self.weapon_display_name(rec), rec.title, rec.kind, self.t("weapon_kind_" + rec.kind), rec.path, rec.rel_path, rec.origin, param_text]).lower()
            if q and q not in hay:
                continue
            self.weapon_filtered.append(rec)
        self.populate_weapon_table()

    def populate_weapon_table(self):
        if not hasattr(self, "weapon_table"):
            return
        self.weapon_table.setSortingEnabled(False)
        self.weapon_table.setRowCount(0)
        t = THEMES[self.theme_key]
        for row, rec in enumerate(self.weapon_filtered):
            m = rec.metrics or {}
            values = [
                self.weapon_display_name(rec),
                self.t("weapon_kind_" + rec.kind),
                format_weapon_number(m.get("theoretical_dps", 0)),
                format_weapon_number(m.get("sustained_dps", 0)),
                format_weapon_number(m.get("burst_1s", 0)),
                format_weapon_number(m.get("score", 0)),
            ]
            self.weapon_table.insertRow(row)
            numeric_values = [None, None, m.get("theoretical_dps", 0), m.get("sustained_dps", 0), m.get("burst_1s", 0), m.get("score", 0)]
            for col, val in enumerate(values):
                item = NumericTableWidgetItem(val, numeric_values[col]) if col >= 2 else QTableWidgetItem(val)
                item.setData(Qt.ItemDataRole.UserRole, row)
                item.setToolTip(str(val))
                if col >= 2:
                    item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                elif col == 1:
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter)
                else:
                    item.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
                if col == 0:
                    f = item.font()
                    f.setBold(True)
                    item.setFont(f)
                if rec.kind == "melee":
                    item.setForeground(QColor(t["accent2"]))
                else:
                    item.setForeground(QColor(t["text"]))
                self.weapon_table.setItem(row, col, item)
        self.weapon_table.setSortingEnabled(True)
        if self.weapon_filtered:
            self.weapon_table.selectRow(0)
        else:
            self.weapon_values_table.setRowCount(0)
            if hasattr(self, "weapon_info_table"):
                self.weapon_info_table.setRowCount(0)
            if hasattr(self, "weapon_metrics_table"):
                self.weapon_metrics_table.setRowCount(0)
            if hasattr(self, "weapon_summary_label"):
                self.weapon_summary_label.setText("")

    def selected_weapon(self) -> Optional[WeaponScriptRecord]:
        if not hasattr(self, "weapon_table"):
            return None
        items = self.weapon_table.selectedItems()
        if not items:
            return None
        try:
            idx = int(items[0].data(Qt.ItemDataRole.UserRole))
        except Exception:
            idx = items[0].row()
        return self.weapon_filtered[idx] if 0 <= idx < len(self.weapon_filtered) else None

    def weapon_display_name(self, rec: WeaponScriptRecord) -> str:
        key = weapon_name_key_from_rel(rec.rel_path or rec.path)
        return self.t(key) if key else rec.title

    def weapon_param_label_text(self, key: str) -> str:
        return self.t(weapon_param_i18n_key(key))

    def readonly_item(self, text: object, bold: bool = False) -> QTableWidgetItem:
        item = QTableWidgetItem(str(text))
        item.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
        if bold:
            f = item.font()
            f.setBold(True)
            item.setFont(f)
        return item

    def set_readonly_rows(self, table: QTableWidget, rows: list[tuple[object, ...]], bold_first_col: bool = True):
        table.setRowCount(0)
        for row, values in enumerate(rows):
            table.insertRow(row)
            for col, value in enumerate(values):
                table.setItem(row, col, self.readonly_item(value, bold=(bold_first_col and col == 0)))

    def load_selected_weapon_values(self):
        rec = self.selected_weapon()
        if not rec or not hasattr(self, "weapon_values_table"):
            return
        t = THEMES[self.theme_key]
        self.weapon_values_table.blockSignals(True)
        self.weapon_values_table.setRowCount(0)
        for row, entry in enumerate(rec.entries):
            self.weapon_values_table.insertRow(row)
            items = [
                QTableWidgetItem(entry.key),
                QTableWidgetItem(self.weapon_param_label_text(entry.key)),
                QTableWidgetItem(entry.value),
                QTableWidgetItem(entry.original),
                QTableWidgetItem(str(entry.line_no + 1)),
            ]
            for col, item in enumerate(items):
                item.setData(Qt.ItemDataRole.UserRole, entry.line_no)
                if col in (2, 3, 4):
                    item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                else:
                    item.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
                if col != 2:
                    item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                if col == 2:
                    f = item.font()
                    f.setBold(True)
                    item.setFont(f)
                item.setForeground(QColor(t["text"]))
                self.weapon_values_table.setItem(row, col, item)
        self.weapon_values_table.blockSignals(False)
        self.update_weapon_performance_panel()

    def current_weapon_overrides(self) -> dict[int, str]:
        overrides: dict[int, str] = {}
        if not hasattr(self, "weapon_values_table"):
            return overrides
        for row in range(self.weapon_values_table.rowCount()):
            value_item = self.weapon_values_table.item(row, 2)
            if value_item is None:
                continue
            line_no = value_item.data(Qt.ItemDataRole.UserRole)
            try:
                overrides[int(line_no)] = value_item.text().strip()
            except Exception:
                pass
        return overrides

    def on_weapon_value_changed(self, item):
        if item is None or item.column() != 2:
            return
        original_item = self.weapon_values_table.item(item.row(), 3)
        t = THEMES[self.theme_key]
        if original_item and item.text().strip() != original_item.text().strip():
            item.setForeground(QColor(t["accent"]))
        else:
            item.setForeground(QColor(t["text"]))
        self.update_weapon_performance_panel(changed=True)

    def update_weapon_performance_panel(self, changed: bool = False):
        if not hasattr(self, "weapon_summary_label"):
            return
        rec = self.selected_weapon()
        if not rec:
            self.weapon_summary_label.setText("")
            for table_name in ("weapon_info_table", "weapon_metrics_table"):
                if hasattr(self, table_name):
                    getattr(self, table_name).setRowCount(0)
            return

        metrics = simulate_weapon_performance(rec, self.current_weapon_overrides())
        self.weapon_summary_label.setText(self.t("weapon_changed_hint") if changed else self.t("weapon_perf_note"))

        display_name = self.weapon_display_name(rec)
        info_rows = [
            (self.t("weapon_col_name"), display_name),
            (self.t("weapon_internal_name"), Path(rec.rel_path or rec.path).name),
            (self.t("weapon_col_kind"), self.t("weapon_kind_" + rec.kind)),
            (self.t("weapon_source"), rec.origin or "-"),
            (self.t("weapon_rel_path"), rec.rel_path or "-"),
            (self.t("detail_path"), str(Path(rec.path))),
        ]
        self.set_readonly_rows(self.weapon_info_table, info_rows)

        metric_rows = [
            (self.t("weapon_metric_damage"), format_weapon_number(metrics.get("damage", 0))),
            (self.t("weapon_metric_cycle"), f"{metrics.get('cycle', 0):.3f}s"),
            (self.t("weapon_metric_clip"), format_weapon_number(metrics.get("clip", 0))),
            (self.t("weapon_metric_reload"), f"{metrics.get('reload', 0):.2f}s"),
            (self.t("weapon_col_dps"), format_weapon_number(metrics.get("theoretical_dps", 0))),
            (self.t("weapon_col_sustained"), format_weapon_number(metrics.get("sustained_dps", 0))),
            (self.t("weapon_col_burst"), format_weapon_number(metrics.get("burst_1s", 0))),
            (self.t("weapon_metric_accuracy"), f"{metrics.get('accuracy_factor', 0):.2f}"),
            (self.t("weapon_metric_score"), format_weapon_number(metrics.get("score", 0))),
        ]
        self.set_readonly_rows(self.weapon_metrics_table, metric_rows)


    def save_selected_weapon(self, show_messages: bool = True) -> bool:
        rec = self.selected_weapon()
        if not rec:
            if show_messages:
                QMessageBox.information(self, APP_NAME, self.t("weapon_select_first"))
            return False

        changed = False
        new_values: dict[int, str] = {}
        for row in range(self.weapon_values_table.rowCount()):
            value_item = self.weapon_values_table.item(row, 2)
            original_item = self.weapon_values_table.item(row, 3)
            if value_item is None:
                continue
            value = value_item.text().strip()
            if not WEAPON_NUMBER_RE.match(value):
                QMessageBox.warning(self, self.t("weapon_save_failed"), self.t("weapon_invalid_number", row=row + 1, value=value))
                return False
            line_no = int(value_item.data(Qt.ItemDataRole.UserRole))
            new_values[line_no] = value
            if original_item and value != original_item.text().strip():
                changed = True

        if not changed:
            if show_messages:
                QMessageBox.information(self, APP_NAME, self.t("weapon_not_changed"))
            return True

        path = Path(rec.path)
        try:
            current_text = path.read_text(encoding="utf-8", errors="replace")
            current_lines = current_text.splitlines(keepends=True)
            entry_by_line = {e.line_no: e for e in rec.entries}
            for line_no, value in new_values.items():
                entry = entry_by_line.get(line_no)
                if entry is None or line_no >= len(current_lines):
                    continue
                current_lines[line_no] = f"{entry.prefix}{value}{entry.suffix}{entry.newline}"

            backup = path.with_name(path.name + ".danyria_backup_" + time.strftime("%Y%m%d_%H%M%S"))
            shutil.copy2(path, backup)
            path.write_text("".join(current_lines), encoding="utf-8", errors="replace")

            refreshed = parse_numeric_weapon_script(path, rec.kind, rec.rel_path, rec.origin, rec.workspace)
            if refreshed:
                for i, old in enumerate(self.weapon_records):
                    if old.path == rec.path:
                        self.weapon_records[i] = refreshed
                        break
                ranked = sorted(self.weapon_records, key=lambda r: r.metrics.get("score", 0), reverse=True)
                for i, item in enumerate(ranked, 1):
                    item.rank = i
                self.apply_weapon_filter()
                for row in range(self.weapon_table.rowCount()):
                    item = self.weapon_table.item(row, 0)
                    if item:
                        try:
                            idx = int(item.data(Qt.ItemDataRole.UserRole))
                            if 0 <= idx < len(self.weapon_filtered) and self.weapon_filtered[idx].path == refreshed.path:
                                self.weapon_table.selectRow(row)
                                break
                        except Exception:
                            pass
            if show_messages:
                QMessageBox.information(self, APP_NAME, self.t("weapon_save_done", backup=str(backup)))
            return True
        except Exception as exc:
            QMessageBox.warning(self, self.t("weapon_save_failed"), str(exc))
            return False

    def reload_selected_weapon(self):
        rec = self.selected_weapon()
        if not rec:
            self.scan_weapon_scripts()
            return
        path = Path(rec.path)
        refreshed = parse_numeric_weapon_script(path, rec.kind, rec.rel_path, rec.origin, rec.workspace)
        if refreshed:
            for i, old in enumerate(self.weapon_records):
                if old.path == rec.path:
                    self.weapon_records[i] = refreshed
                    break
            ranked = sorted(self.weapon_records, key=lambda r: r.metrics.get("score", 0), reverse=True)
            for i, item in enumerate(ranked, 1):
                item.rank = i
            self.apply_weapon_filter()

    def open_scripts_folder(self):
        root = self.get_l4d2()
        if root:
            p = root / "scripts"
            p.mkdir(parents=True, exist_ok=True)
            self.open_path(p)

    def open_selected_weapon_file(self):
        rec = self.selected_weapon()
        if rec:
            self.open_path(Path(rec.path))
        else:
            QMessageBox.information(self, APP_NAME, self.t("weapon_select_first"))

    def find_weapon_vpk_sources(self, root: Path) -> list[Path]:
        candidates: list[Path] = []

        def add(p: Path):
            if p.exists() and p.is_file() and p.suffix.lower() == ".vpk":
                low_name = p.name.lower()
                if low_name == "danyria_weapon_values.vpk":
                    return
                if re.search(r"_\d{3}\.vpk$", low_name):
                    return
                if p not in candidates:
                    candidates.append(p)

        search_dirs = [root]
        parent = root.parent
        for name in ["left4dead2_dlc1", "left4dead2_dlc2", "left4dead2_dlc3", "update"]:
            d = parent / name
            if d.exists():
                search_dirs.append(d)
        for d in sorted(parent.glob("left4dead2*")):
            if d.is_dir() and d not in search_dirs:
                search_dirs.append(d)

        for d in search_dirs:
            add(d / "pak01_dir.vpk")

        addons = root / "addons"
        if addons.exists():
            for p in sorted(addons.rglob("*.vpk")):
                add(p)
        return candidates

    def extract_weapon_scripts_from_vpks(self, custom_sources: Optional[list[Path]] = None):
        root = self.get_l4d2()
        if not root:
            return

        if custom_sources is None or isinstance(custom_sources, bool):
            sources = self.find_weapon_vpk_sources(root)
        elif isinstance(custom_sources, (str, Path)):
            sources = [Path(custom_sources)]
        else:
            sources = list(custom_sources)
        sources = [Path(p) for p in sources if Path(p).exists() and Path(p).is_file() and Path(p).suffix.lower() == ".vpk"]
        extracted: dict[str, tuple[bytes, str]] = {}
        hit_sources: set[str] = set()

        for vpk in sources:
            names, entries, valid, note, data_base = parse_vpk(vpk)
            if not valid or not entries:
                continue
            local_hits = 0
            for rel in sorted(entries.keys()):
                if not is_weapon_script_rel(rel):
                    continue
                data = read_vpk_file(vpk, entries, data_base, rel)
                if not data:
                    continue
                extracted[rel.lower().replace("\\", "/")] = (data, str(vpk))
                local_hits += 1
            if local_hits:
                hit_sources.add(str(vpk))

        if not extracted:
            QMessageBox.information(self, self.t("weapon_vpk_extract_title"), self.t("weapon_vpk_extract_none"))
            return

        project = self.weapon_project_dir()
        scripts_dir = project / "scripts"
        if scripts_dir.exists():
            backup = project.with_name(project.name + ".backup_" + time.strftime("%Y%m%d_%H%M%S"))
            try:
                shutil.copytree(project, backup)
            except Exception:
                pass
            try:
                shutil.rmtree(scripts_dir)
            except Exception:
                pass
        project.mkdir(parents=True, exist_ok=True)

        source_map = {}
        for rel, (data, src) in sorted(extracted.items()):
            out = project / rel
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_bytes(data)
            source_map[rel] = src
        ensure_weapon_addoninfo(project)
        try:
            (project / "danyria_weapon_sources.json").write_text(json.dumps(source_map, ensure_ascii=False, indent=2), encoding="utf-8")
        except Exception:
            pass

        self.scan_weapon_scripts(silent=True)
        if hasattr(self, "weapon_workspace_path_edit"):
            self.weapon_workspace_path_edit.setText(str(project))
            self.weapon_workspace_path_edit.setToolTip(str(project))
        if hasattr(self, "weapon_summary_label"):
            self.weapon_summary_label.setText(
                self.t("weapon_vpk_extract_done", sources=len(hit_sources), files=len(extracted), folder=str(project)) +
                "\n" + self.t("weapon_perf_note")
            )
        QMessageBox.information(
            self,
            self.t("weapon_vpk_extract_title"),
            self.t("weapon_vpk_extract_done", sources=len(hit_sources), files=len(extracted), folder=str(project))
        )

    def pack_weapon_values_vpk(self):
        root = self.get_l4d2()
        if not root:
            return

        if self.selected_weapon() and not self.save_selected_weapon(show_messages=False):
            return

        project = self.weapon_project_dir()
        scripts_dir = project / "scripts"
        script_files = []
        if scripts_dir.exists():
            for p in sorted(scripts_dir.rglob("*.txt")):
                rel = p.relative_to(project).as_posix().lower()
                if is_weapon_script_rel(rel):
                    script_files.append((rel, p))
        if not script_files:
            QMessageBox.information(self, APP_NAME, self.t("weapon_vpk_pack_empty"))
            return

        dlg, layout = self.create_themed_dialog(self.t("weapon_pack_dialog_title"), min_width=780, size=(820, 560))
        hint = QLabel(self.t("weapon_pack_dialog_hint"))
        hint.setObjectName("TinyText")
        hint.setWordWrap(True)
        layout.addWidget(hint)

        def normalize_weapon_pack_name(raw: str) -> str:
            safe = re.sub(r'[<>:"/\\|?*]+', "_", Path(raw or "").name).strip(" .")
            if not safe:
                safe = "danyria_weapon_values.vpk"
            if not safe.lower().endswith(".vpk"):
                safe += ".vpk"
            return safe

        name_row = QHBoxLayout()
        name_label = QLabel(self.t("weapon_pack_name_label"))
        self.weapon_pack_name_edit = QLineEdit("danyria_weapon_values.vpk")
        name_row.addWidget(name_label)
        name_row.addWidget(self.weapon_pack_name_edit, 1)
        layout.addLayout(name_row)

        out_row = QHBoxLayout()
        out_label = QLabel(self.t("weapon_pack_output_path_label"))
        self.weapon_pack_output_path_edit = QLineEdit()
        self.weapon_pack_output_path_edit.setObjectName("WeaponPackPathEdit")
        self.weapon_pack_output_path_edit.setReadOnly(True)
        out_row.addWidget(out_label)
        out_row.addWidget(self.weapon_pack_output_path_edit, 1)
        layout.addLayout(out_row)

        def refresh_weapon_pack_output_path():
            out_path = root / "addons" / normalize_weapon_pack_name(self.weapon_pack_name_edit.text())
            self.weapon_pack_output_path_edit.setText(str(out_path))
            self.weapon_pack_output_path_edit.setToolTip(str(out_path))

        self.weapon_pack_name_edit.textChanged.connect(refresh_weapon_pack_output_path)
        refresh_weapon_pack_output_path()

        files_table = SmoothTableWidget(0, 3)
        files_table.setObjectName("WeaponPackTable")
        files_table.setHorizontalHeaderLabels([
            self.t("weapon_pack_col_include"),
            self.t("weapon_pack_col_path"),
            self.t("weapon_pack_col_size"),
        ])
        files_table.verticalHeader().setVisible(False)
        files_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        files_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        files_table.setAlternatingRowColors(True)
        files_table.setShowGrid(True)
        self.make_columns_resizable(files_table, [90, 520, 110])
        for row, (rel, p) in enumerate(script_files):
            files_table.insertRow(row)
            chk_item = QTableWidgetItem("")
            chk_item.setFlags(Qt.ItemFlag.ItemIsEnabled)
            files_table.setItem(row, 0, chk_item)
            chk = QCheckBox()
            chk.setChecked(True)
            chk.setToolTip(rel)
            chk_wrap = QWidget()
            chk_wrap.setObjectName("PackCheckCell")
            chk_l = QHBoxLayout(chk_wrap)
            chk_l.setContentsMargins(0, 0, 0, 0)
            chk_l.setSpacing(0)
            chk_l.addStretch(1)
            chk_l.addWidget(chk)
            chk_l.addStretch(1)
            files_table.setCellWidget(row, 0, chk_wrap)
            path_item = QTableWidgetItem(rel)
            path_item.setData(Qt.ItemDataRole.UserRole, rel)
            files_table.setItem(row, 1, path_item)
            try:
                size_text = f"{p.stat().st_size / 1024:.1f} KB"
            except Exception:
                size_text = "-"
            size_item = QTableWidgetItem(size_text)
            size_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            files_table.setItem(row, 2, size_item)
        layout.addWidget(files_table, 1)

        def set_pack_checks(checked: bool):
            for r in range(files_table.rowCount()):
                wrap = files_table.cellWidget(r, 0)
                cb = wrap.findChild(QCheckBox) if wrap is not None else None
                if cb is not None:
                    cb.setChecked(bool(checked))

        def toggle_pack_check(row: int, col: int):
            if col != 0:
                return
            wrap = files_table.cellWidget(row, 0)
            cb = wrap.findChild(QCheckBox) if wrap is not None else None
            if cb is not None:
                cb.setChecked(not cb.isChecked())

        files_table.cellClicked.connect(toggle_pack_check)

        select_row = QHBoxLayout()
        select_all_btn = self.button(self.t("weapon_pack_select_all"), lambda: set_pack_checks(True))
        select_none_btn = self.button(self.t("weapon_pack_select_none"), lambda: set_pack_checks(False))
        select_row.addWidget(select_all_btn)
        select_row.addWidget(select_none_btn)
        select_row.addStretch(1)
        ok_btn = self.button(self.t("weapon_pack_confirm"), dlg.accept, accent=True)
        cancel_btn = self.button(self.t("cancel"), dlg.reject)
        select_row.addWidget(ok_btn)
        select_row.addWidget(cancel_btn)
        layout.addLayout(select_row)

        if dlg.exec() != QDialog.DialogCode.Accepted:
            return

        safe_name = normalize_weapon_pack_name(self.weapon_pack_name_edit.text())

        selected_rels = []
        for row in range(files_table.rowCount()):
            wrap = files_table.cellWidget(row, 0)
            cb = wrap.findChild(QCheckBox) if wrap is not None else None
            rel_item = files_table.item(row, 1)
            if cb is not None and rel_item and cb.isChecked():
                selected_rels.append(str(rel_item.data(Qt.ItemDataRole.UserRole) or rel_item.text()))
        if not selected_rels:
            QMessageBox.information(self, APP_NAME, self.t("weapon_pack_select_empty"))
            return

        try:
            addons = root / "addons"
            addons.mkdir(parents=True, exist_ok=True)
            dest_vpk = addons / safe_name
            temp_dir = project / ".danyria_pack_selection"
            if temp_dir.exists():
                shutil.rmtree(temp_dir, ignore_errors=True)
            temp_dir.mkdir(parents=True, exist_ok=True)
            for rel in selected_rels:
                src = project / rel
                if not src.exists() or not is_weapon_script_rel(rel):
                    continue
                out = temp_dir / rel
                out.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src, out)
            ensure_weapon_addoninfo(temp_dir)

            temp_vpk = temp_dir.with_suffix(".vpk")
            if temp_vpk.exists():
                temp_vpk.unlink()
            packed = None
            vpk_exe = self.find_vpk_exe(root)
            if vpk_exe:
                try:
                    subprocess.run([str(vpk_exe), str(temp_dir)], cwd=str(temp_dir.parent), check=True)
                    if temp_vpk.exists():
                        packed = temp_vpk
                except Exception:
                    packed = None

            if dest_vpk.exists():
                self.backup_existing_path(dest_vpk)
            if packed and packed.exists():
                shutil.copy2(packed, dest_vpk)
            else:
                write_simple_vpk(temp_dir, dest_vpk)
            try:
                shutil.rmtree(temp_dir, ignore_errors=True)
                if temp_vpk.exists():
                    temp_vpk.unlink()
            except Exception:
                pass

            self.scan()
            self.scan_weapon_scripts(silent=True)
            QMessageBox.information(self, self.t("weapon_vpk_pack_title"), self.t("weapon_vpk_pack_done", path=str(dest_vpk)))
        except Exception as exc:
            QMessageBox.warning(self, self.t("weapon_vpk_pack_failed"), str(exc))

    def open_weapon_workspace(self):
        project = self.weapon_project_dir()
        project.mkdir(parents=True, exist_ok=True)
        self.open_path(project)

    def hud_plugin_count(self):
        root = self.get_l4d2(silent=True)
        if not root:
            return None
        paths = [
            root / "addons" / "danyria_hud_plugin",
            root / "addons" / "danyria_hud_plugin.vpk",
            root / "addons" / "danyria_hud_plugin.vpk.disabled",
            root / "addons" / "danyria_hud_plugin.disabled",
            root / "addons" / "_danyria_disabled" / "danyria_hud_plugin",
            root / "addons" / "_danyria_disabled" / "danyria_hud_plugin.vpk",
        ]
        return 1 if any(p.exists() for p in paths) else 0

    def update_hud_plugin_status(self):
        if not hasattr(self, "hud_plugin_status_label"):
            return
        count = self.hud_plugin_count()
        if count is None:
            text = self.t("hud_plugin_unknown")
        elif count:
            text = self.t("hud_plugin_installed", n=count)
        else:
            text = self.t("hud_plugin_missing")
        self.plugin_card.set_status_text(text)

    def penalty_plugin_count(self):
        root = self.get_l4d2(silent=True)
        if not root:
            return None
        paths = [
            root / "addons" / "danyria_penalty_plugin",
            root / "addons" / "danyria_penalty_plugin.vpk",
            root / "addons" / "danyria_penalty_plugin.vpk.disabled",
            root / "addons" / "danyria_penalty_plugin.disabled",
            root / "addons" / "_danyria_disabled" / "danyria_penalty_plugin",
            root / "addons" / "_danyria_disabled" / "danyria_penalty_plugin.vpk",
        ]
        return 1 if any(p.exists() for p in paths) else 0

    def update_penalty_plugin_status(self):
        if not hasattr(self, "penalty_plugin_status_label"):
            return
        count = self.penalty_plugin_count()
        if count is None:
            text = self.t("penalty_plugin_unknown")
        elif count:
            text = self.t("penalty_plugin_installed", n=count)
        else:
            text = self.t("penalty_plugin_missing")
        self.penalty_card.set_status_text(text)

    def button(self, text, cb, accent=False):
        b = QPushButton(text)
        b.setMinimumHeight(32)
        b.setMinimumWidth(96)
        b.setMaximumWidth(170)
        b.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        b.clicked.connect(cb)
        if accent:
            b.setProperty("accent", True)
        return b

    def group_label(self, text: str) -> QLabel:
        label = QLabel(text)
        label.setObjectName("GroupLabel")
        return label

    def add_button_group(self, layout: QVBoxLayout, title: str, buttons: list[QPushButton], extra_widget: Optional[QWidget] = None):
        layout.addWidget(self.group_label(title))
        box = QFrame(objectName="ButtonGroup")
        box.setMinimumWidth(238)
        box.setMaximumWidth(246)
        box.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        box_l = QVBoxLayout(box)
        box_l.setContentsMargins(6, 6, 6, 6)
        box_l.setSpacing(6)
        if extra_widget is not None:
            extra_widget.setMinimumWidth(222)
            extra_widget.setMaximumWidth(232)
            box_l.addWidget(extra_widget)
        for btn in buttons:
            btn.setMinimumHeight(34)
            btn.setMinimumWidth(222)
            btn.setMaximumWidth(232)
            btn.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
            box_l.addWidget(btn)
        layout.addWidget(box, 0, Qt.AlignmentFlag.AlignLeft)
        return box

    def set_button_icon(self, btn: QPushButton, path: Path, size: int = 26):
        if path.exists():
            btn.setIcon(QIcon(str(path)))
            btn.setIconSize(QSize(size, size))
            btn.setText("")

    def load_branding(self):
        try:
            self.avatar.setGraphicsEffect(None)
            self.brand_logo.setGraphicsEffect(None)
        except Exception:
            pass

        self.avatar.set_image(self.icon_path_for_theme())

        t = THEMES[self.theme_key]
        title_col = t.get("brand_title", "#6FADE8")
        ver_col = t.get("brand_version", "#EA6FBE")
        self.brand_logo.set_theme_colors(title_col, ver_col)
        self.brand_logo.set_version(APP_VERSION, self.t("version_label"))

        if hasattr(self, "settings_btn"):
            self.settings_btn.setToolTip(self.t("settings"))
        self.apply_icon()

    def apply_theme(self, key, initial=False):
        self.theme_key = key if key in THEMES else "normal"
        t = THEMES[self.theme_key]

        try:
            self.setUpdatesEnabled(False)
        except Exception:
            pass

        self.setStyleSheet(self.qss(t))
        if self.cursor_overlay:
            self.cursor_overlay.set_theme(self.theme_key, t)

        if not initial:
            self.save_config()

        self.load_branding()
        self.update_language()
        self.refresh_table_colors()
        if hasattr(self, "weapon_table"):
            self.populate_weapon_table()

        try:
            self.setUpdatesEnabled(True)
            self.update()
        except Exception:
            pass

        if self.cursor_overlay:
            self.sync_overlay_geometry()
        if not initial:
            self.animate_theme_switch()

    def toggle_theme(self):
        self.apply_theme("ruin" if self.theme_key == "normal" else "normal")

    def toggle_maximize(self):
        if self.isMaximized():
            self.showNormal()
            if hasattr(self.max_btn, "set_icon_kind"):
                self.max_btn.set_icon_kind("maximize")
        else:
            self._resizing_edges = None
            self.showMaximized()
            if hasattr(self.max_btn, "set_icon_kind"):
                self.max_btn.set_icon_kind("restore")


    def keep_animation(self, anim):
        self._animations.append(anim)
        anim.finished.connect(lambda a=anim: self._animations.remove(a) if a in self._animations else None)
        anim.start()

    def ease(self):
        return QEasingCurve(QEasingCurve.Type.OutCubic)

    def animate_opacity(self, widget, start=0.0, end=1.0, duration=120, delay=0):
        try:
            if widget is not None:
                widget.setGraphicsEffect(None)
        except Exception:
            pass

    def animate_slide_in(self, widget, dy=0, duration=0, delay=0):
        return

    def animate_page_transition(self, widget):
        try:
            if widget is not None:
                effect = QGraphicsOpacityEffect(widget)
                widget.setGraphicsEffect(effect)
                anim = QPropertyAnimation(effect, b"opacity", self)
                anim.setDuration(150)
                anim.setStartValue(0.0)
                anim.setEndValue(1.0)
                anim.setEasingCurve(QEasingCurve(QEasingCurve.Type.OutCubic))

                def clear_effect():
                    try:
                        widget.setGraphicsEffect(None)
                    except Exception:
                        pass

                anim.finished.connect(clear_effect)
                self.keep_animation(anim)
        except Exception:
            pass

    def start_entry_animations(self):
        if getattr(self, "_entry_animation_done", False):
            return
        self._entry_animation_done = True
        try:
            self.setWindowOpacity(0.0)
            anim = QPropertyAnimation(self, b"windowOpacity", self)
            anim.setStartValue(0.0)
            anim.setEndValue(1.0)
            anim.setDuration(260)
            anim.setEasingCurve(QEasingCurve(QEasingCurve.Type.OutCubic))
            self.keep_animation(anim)
        except Exception:
            try:
                self.setWindowOpacity(1.0)
            except Exception:
                pass

    def animate_theme_switch(self):
        try:
            effect = QGraphicsOpacityEffect(self.window_frame)
            self.window_frame.setGraphicsEffect(effect)
            anim = QPropertyAnimation(effect, b"opacity", self)
            anim.setDuration(180)
            anim.setStartValue(0.84)
            anim.setEndValue(1.0)
            anim.setEasingCurve(QEasingCurve(QEasingCurve.Type.OutCubic))

            def clear_effect():
                try:
                    self.window_frame.setGraphicsEffect(None)
                except Exception:
                    pass

            anim.finished.connect(clear_effect)
            self.keep_animation(anim)
        except Exception:
            pass

    def animate_table_update(self):
        return


    def _global_pos_from_event(self, event):
        try:
            return event.globalPosition().toPoint()
        except Exception:
            return event.globalPos()

    def _resize_edges_at(self, global_pos):
        if self.isMaximized() or self.isFullScreen():
            return None
        g = self.frameGeometry()
        x = global_pos.x()
        y = global_pos.y()
        m = getattr(self, "_resize_margin", 8)
        left = abs(x - g.left()) <= m
        right = abs(x - g.right()) <= m
        top = abs(y - g.top()) <= m
        bottom = abs(y - g.bottom()) <= m
        if not (left or right or top or bottom):
            return None
        return {"left": left, "right": right, "top": top, "bottom": bottom}

    def _cursor_for_edges(self, edges):
        if not edges:
            return Qt.CursorShape.ArrowCursor
        left = edges.get("left")
        right = edges.get("right")
        top = edges.get("top")
        bottom = edges.get("bottom")
        if (left and top) or (right and bottom):
            return Qt.CursorShape.SizeFDiagCursor
        if (right and top) or (left and bottom):
            return Qt.CursorShape.SizeBDiagCursor
        if left or right:
            return Qt.CursorShape.SizeHorCursor
        if top or bottom:
            return Qt.CursorShape.SizeVerCursor
        return Qt.CursorShape.ArrowCursor

    def _apply_resize_from_global_pos(self, global_pos):
        edges = getattr(self, "_resizing_edges", None)
        if not edges or self._resize_start_pos is None or self._resize_start_geo is None:
            return
        delta = global_pos - self._resize_start_pos
        geom = self._resize_start_geo
        min_w = max(1, self.minimumWidth())
        min_h = max(1, self.minimumHeight())

        left = geom.left()
        right = geom.right()
        top = geom.top()
        bottom = geom.bottom()

        if edges.get("left"):
            left = min(geom.left() + delta.x(), geom.right() - min_w + 1)
        if edges.get("right"):
            right = max(geom.right() + delta.x(), geom.left() + min_w - 1)
        if edges.get("top"):
            top = min(geom.top() + delta.y(), geom.bottom() - min_h + 1)
        if edges.get("bottom"):
            bottom = max(geom.bottom() + delta.y(), geom.top() + min_h - 1)

        self.setGeometry(left, top, right - left + 1, bottom - top + 1)

    def sync_overlay_geometry(self):
        if not self.cursor_overlay:
            return
        self.cursor_overlay.setGeometry(0, 0, self.width(), self.height())
        self.cursor_overlay.raise_()

    def showEvent(self, event):
        super().showEvent(event)
        QTimer.singleShot(0, self.sync_overlay_geometry)
        QTimer.singleShot(20, self.start_entry_animations)
        QTimer.singleShot(60, self.sync_overlay_geometry)

    def install_mouse_tracking(self, widget):
        try:
            widget.setMouseTracking(True)
        except Exception:
            pass
        for child in widget.findChildren(QWidget):
            try:
                child.setMouseTracking(True)
            except Exception:
                pass

    def eventFilter(self, obj, event):
        try:
            etype = event.type()
            inside_window = isinstance(obj, QWidget) and (obj is self or self.isAncestorOf(obj))
            if inside_window:
                if etype == QEvent.Type.MouseButtonPress and event.button() == Qt.MouseButton.LeftButton:
                    gpos = self._global_pos_from_event(event)
                    edges = self._resize_edges_at(gpos)
                    if edges:
                        self._resizing_edges = edges
                        self._resize_start_pos = gpos
                        self._resize_start_geo = self.frameGeometry()
                        self.setCursor(self._cursor_for_edges(edges))
                        event.accept()
                        return True

                if etype == QEvent.Type.MouseMove:
                    gpos = self._global_pos_from_event(event)
                    if getattr(self, "_resizing_edges", None):
                        self._apply_resize_from_global_pos(gpos)
                        event.accept()
                        return True
                    if not (event.buttons() & Qt.MouseButton.LeftButton):
                        edges = self._resize_edges_at(gpos)
                        self.setCursor(self._cursor_for_edges(edges))

                if etype == QEvent.Type.MouseButtonRelease and getattr(self, "_resizing_edges", None):
                    self._resizing_edges = None
                    self._resize_start_pos = None
                    self._resize_start_geo = None
                    self.setCursor(Qt.CursorShape.ArrowCursor)
                    event.accept()
                    return True

                if self.cursor_overlay and etype in (QEvent.Type.MouseMove, QEvent.Type.MouseButtonPress):
                    if not getattr(self, "_resizing_edges", None):
                        self.sync_overlay_geometry()
                        gpos = self._global_pos_from_event(event)
                        local = self.cursor_overlay.mapFromGlobal(gpos)
                        if self.cursor_overlay.rect().contains(local):
                            if etype == QEvent.Type.MouseMove:
                                self.cursor_overlay.add_trail(local)
                            else:
                                self.cursor_overlay.add_click(local)
        except Exception:
            pass
        return super().eventFilter(obj, event)

    def mousePressEvent(self, event):
        try:
            if event.button() == Qt.MouseButton.LeftButton:
                gpos = self._global_pos_from_event(event)
                edges = self._resize_edges_at(gpos)
                if edges:
                    self._resizing_edges = edges
                    self._resize_start_pos = gpos
                    self._resize_start_geo = self.frameGeometry()
                    self.setCursor(self._cursor_for_edges(edges))
                    event.accept()
                    return
        except Exception:
            pass
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        try:
            gpos = self._global_pos_from_event(event)
            if getattr(self, "_resizing_edges", None):
                self._apply_resize_from_global_pos(gpos)
                event.accept()
                return
            if not (event.buttons() & Qt.MouseButton.LeftButton):
                self.setCursor(self._cursor_for_edges(self._resize_edges_at(gpos)))
        except Exception:
            pass
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        try:
            if getattr(self, "_resizing_edges", None):
                self._resizing_edges = None
                self._resize_start_pos = None
                self._resize_start_geo = None
                self.setCursor(Qt.CursorShape.ArrowCursor)
                event.accept()
                return
        except Exception:
            pass
        super().mouseReleaseEvent(event)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.sync_overlay_geometry()

    def auto_detect_path(self, force: bool = False):
        if not force and self.l4d2:
            return
        for p in candidate_l4d2_paths():
            if p.exists() and (p / "addons").exists():
                self.l4d2 = p
                self.config["l4d2_path_manual"] = False
                self.save_config()
                return

    def auto_detect_click(self):
        self.auto_detect_path(force=True)
        if self.l4d2:
            self.path_edit.setText(str(self.l4d2))
            QMessageBox.information(self, APP_NAME, self.t("auto_detect_ok"))
        else:
            QMessageBox.warning(self, APP_NAME, self.t("auto_detect_fail"))

    def choose_path(self):
        path = QFileDialog.getExistingDirectory(self, self.t("choose_l4d2_folder"))
        if path:
            self.l4d2 = Path(path)
            self.config["l4d2_path_manual"] = True
            self.path_edit.setText(str(self.l4d2))
            self.save_config()
            self.scan()

    def get_l4d2(self, silent: bool = False):
        raw = self.path_edit.text().strip()
        if raw:
            self.l4d2 = Path(raw)

        if not self.l4d2 or not self.l4d2.exists():
            if not silent:
                QMessageBox.warning(self, self.t("path"), self.t("missing_path"))
            return None

        if not (self.l4d2 / "addons").exists():
            if not silent:
                QMessageBox.warning(self, self.t("path"), self.t("path_no_addons"))
            return None

        if not silent:
            self.save_config()
        return self.l4d2

    def scan_cache_key(self, path: Path) -> str:
        try:
            return str(path.resolve()).lower()
        except Exception:
            return str(path).lower()

    def scan_target_fingerprint(self, path: Path) -> tuple:
        try:
            st = path.stat()
            mtime = getattr(st, "st_mtime_ns", int(st.st_mtime * 1_000_000_000))
            if path.is_file():
                return ("file", st.st_size, mtime)
            if path.is_dir():
                latest = mtime
                count = 0
                try:
                    for child in path.iterdir():
                        count += 1
                        if count <= 160:
                            cst = child.stat()
                            latest = max(latest, getattr(cst, "st_mtime_ns", int(cst.st_mtime * 1_000_000_000)))
                except Exception:
                    pass
                info_size = 0
                info_mtime = 0
                info = path / "addoninfo.txt"
                try:
                    if info.exists():
                        ist = info.stat()
                        info_size = ist.st_size
                        info_mtime = getattr(ist, "st_mtime_ns", int(ist.st_mtime * 1_000_000_000))
                except Exception:
                    pass
                return ("dir", mtime, latest, count, info_size, info_mtime)
        except Exception:
            pass
        return ("missing",)

    def scan_cached_target(self, path: Path, root: Path) -> tuple[str, Optional[ModRecord]]:
        key = self.scan_cache_key(path)
        fingerprint = self.scan_target_fingerprint(path)
        cached = self._scan_cache.get(key)
        if cached and cached[0] == fingerprint:
            rec = cached[1]
            return key, replace(rec) if rec else None

        rec = scan_one(path, root)
        self._scan_cache[key] = (fingerprint, replace(rec) if rec else None)
        return key, rec

    def scan(self):
        root = self.get_l4d2()
        if not root:
            return
        root_key = self.scan_cache_key(root)
        if self._scan_cache_root != root_key:
            self._scan_cache = {}
            self._scan_cache_root = root_key

        records = []
        seen_cache_keys = set()
        for folder in [root / "addons", root / "addons" / "workshop"]:
            if not folder.exists():
                continue
            for child in folder.iterdir():
                low_name = child.name.lower()
                if low_name in ("workshop", "_danyria_disabled", "_danyria_backups"):
                    continue
                if ".backup_" in low_name or low_name.endswith(".danyria_backup"):
                    continue
                key, rec = self.scan_cached_target(child, root)
                seen_cache_keys.add(key)
                if rec:
                    records.append(rec)

        disabled_stash = root / "addons" / "_danyria_disabled"
        if disabled_stash.exists():
            for child in disabled_stash.iterdir():
                key, rec = self.scan_cached_target(child, root)
                seen_cache_keys.add(key)
                if rec:
                    rec.status = "Disabled"
                    rec.source = "Local"
                    disabled_note = "disabled folder stored in addons/_danyria_disabled"
                    if disabled_note not in rec.evidence:
                        rec.evidence.insert(0, disabled_note)
                    records.append(rec)

        try:
            records = self.merge_workshop_manifest_records(root, records)
        except Exception:
            pass

        self._scan_cache = {k: v for k, v in self._scan_cache.items() if k in seen_cache_keys}

        self.records = sorted(records, key=lambda x: (x.source != "Workshop", x.category, x.title.lower()))
        self.refresh_filters()
        self.apply_filter()
        plugin_types = set()
        for x in records:
            hay = (x.path + " " + x.title).lower()
            if "danyria_hud_plugin" in hay or "danyria hud" in hay:
                plugin_types.add("hud")
            if "danyria_penalty_plugin" in hay or "score system" in hay or "评分" in hay:
                plugin_types.add("score")
        self.last_scan_count = len(records)
        self.last_danyria_count = len(plugin_types)
        self.update_status_text()
        self.update_hud_plugin_status()
        if hasattr(self, "update_penalty_plugin_status"):
            self.update_penalty_plugin_status()

    def refresh_filters(self):
        cur = self.cat_filter.currentData() if hasattr(self, "cat_filter") else "__all__"
        cats = sorted(set(x.category for x in self.records))
        self.cat_filter.blockSignals(True)
        self.cat_filter.clear()
        self.cat_filter.addItem(self.t("filter_all_categories"), "__all__")
        for cat in cats:
            self.cat_filter.addItem(self.tr_category(cat), cat)
        for i in range(self.cat_filter.count()):
            if self.cat_filter.itemData(i) == cur:
                self.cat_filter.setCurrentIndex(i)
                break
        self.cat_filter.blockSignals(False)

    def apply_filter(self):
        q = self.search.text().strip().lower()
        cat = self.cat_filter.currentData() if hasattr(self, "cat_filter") else "__all__"
        source = self.source_filter.currentData() if hasattr(self, "source_filter") else "__all__"
        status = self.status_filter.currentData() if hasattr(self, "status_filter") else "__all__"
        self.filtered = []
        for r in self.records:
            if cat != "__all__" and r.category != cat:
                continue
            if source != "__all__" and r.source != source:
                continue
            if status != "__all__" and r.status != status:
                continue
            hay = " ".join([r.title, r.workshop_id, r.category, self.tr_category(r.category), r.kind, self.tr_kind(r.kind), r.source, self.tr_source(r.source), r.status, self.tr_status(r.status), r.path, r.author, r.description, " ".join(r.tags), " ".join(r.evidence)]).lower()
            if q and q not in hay:
                continue
            self.filtered.append(r)
        self.populate_table()

    def refresh_table_colors(self):
        if not hasattr(self, "table"):
            return
        t = THEMES[self.theme_key]
        for row in range(self.table.rowCount()):
            rec = None
            first = self.table.item(row, 0)
            if first is not None:
                try:
                    idx = int(first.data(Qt.ItemDataRole.UserRole))
                    if 0 <= idx < len(self.filtered):
                        rec = self.filtered[idx]
                except Exception:
                    rec = None

            for col in range(self.table.columnCount()):
                item = self.table.item(row, col)
                if item is None:
                    continue
                if rec and rec.category == "Danyria":
                    item.setForeground(QColor(t["accent"]))
                elif rec and rec.status == "Broken":
                    item.setForeground(QColor(t["danger"]))
                elif rec and rec.status == "Disabled":
                    item.setForeground(QColor(t["subtle"]))
                else:
                    item.setForeground(QColor(t["text"]))

    def display_mod_status(self, rec: ModRecord) -> str:
        if rec.source == "Workshop":
            if rec.status == "Missing":
                return self.t("workshop_badge_missing")
            if rec.status == "Subscribed":
                return self.t("workshop_badge_subscribed")
            if rec.status == "Disabled":
                return self.t("workshop_badge_disabled")
            if rec.status == "Enabled":
                return self.t("workshop_badge_local")
            return self.t("workshop_badge_unknown")
        return self.tr_status(rec.status)

    def display_mod_source(self, rec: ModRecord) -> str:
        if rec.source == "Workshop":
            return self.tr_source(rec.source)
        return self.tr_source(rec.source)

    def populate_table(self):
        if not hasattr(self, "table"):
            return
        self.table.setSortingEnabled(False)
        self.table.setRowCount(0)
        t = THEMES[self.theme_key]
        for row, rec in enumerate(self.filtered):
            self.table.insertRow(row)
            evidence_short = rec.workshop_id or ", ".join(rec.tags) or (rec.evidence[0] if rec.evidence else "")
            values = [
                rec.title,
                self.tr_category(rec.category),
                self.display_mod_status(rec),
                self.tr_kind(rec.kind),
                self.display_mod_source(rec),
                f"{rec.size_mb:.2f} MB",
                evidence_short,
            ]
            for col, val in enumerate(values):
                item = QTableWidgetItem(val)
                item.setData(Qt.ItemDataRole.UserRole, row)
                if col in (1, 2, 3, 4):
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter)
                elif col == 5:
                    item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                else:
                    item.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
                if col == 0:
                    f = item.font()
                    f.setBold(True)
                    item.setFont(f)
                if rec.category == "Danyria":
                    item.setForeground(QColor(t["accent"]))
                elif rec.status == "Broken":
                    item.setForeground(QColor(t["danger"]))
                elif rec.status == "Disabled":
                    item.setForeground(QColor(t["subtle"]))
                elif rec.status in ("Subscribed", "Missing"):
                    item.setForeground(QColor(t["accent2"]))
                self.table.setItem(row, col, item)
        self.table.setSortingEnabled(True)
        if self.filtered:
            self.table.selectRow(0)
        else:
            self.details.clear()
        self.animate_table_update()

    def is_workshop_record(self, rec: ModRecord) -> bool:
        try:
            if getattr(rec, "workshop_id", ""):
                return True
            if str(getattr(rec, "source", "")).lower() == "workshop":
                return True
            p = str(getattr(rec, "path", "")).lower().replace("/", "\\")
            return "\\addons\\workshop\\" in p or "\\workshop\\content\\550\\" in p
        except Exception:
            return False

    def selected_records(self) -> list[ModRecord]:
        if not hasattr(self, "table"):
            return []
        rows = []
        try:
            rows = sorted({idx.row() for idx in self.table.selectionModel().selectedRows()})
        except Exception:
            rows = sorted({item.row() for item in self.table.selectedItems()})
        records = []
        for row in rows:
            item = self.table.item(row, 0)
            if item is None:
                continue
            try:
                idx = int(item.data(Qt.ItemDataRole.UserRole))
            except Exception:
                idx = row
            if 0 <= idx < len(self.filtered):
                records.append(self.filtered[idx])
        return records

    def select_all_mods(self):
        if hasattr(self, "table"):
            self.table.selectAll()

    def selected(self):
        recs = self.selected_records()
        return recs[0] if recs else None

    def update_details(self):
        rec = self.selected()
        if not rec:
            self.details.clear()
            return
        c = self.t("colon")
        lines = [
            f"{self.t('detail_name')}{c}{rec.title}",
            f"{self.t('detail_category')}{c}{self.tr_category(rec.category)}",
            f"{self.t('detail_status')}{c}{self.display_mod_status(rec)}",
            f"{self.t('detail_type')}{c}{self.tr_kind(rec.kind)}",
            f"{self.t('detail_source')}{c}{self.display_mod_source(rec)}",
            f"{self.t('detail_size')}{c}{rec.size_mb:.2f} MB",
            f"{self.t('detail_workshop_id')}{c}{rec.workshop_id or '-'}",
            *(([f"{self.t('detail_workshop_manage')}{c}{self.t('workshop_manage_hint')}"] if rec.source == "Workshop" else [])),
            f"{self.t('detail_author')}{c}{rec.author or '-'}",
            f"{self.t('detail_modified')}{c}{rec.modified}",
            f"{self.t('detail_tags')}{c}{', '.join(rec.tags) if rec.tags else '-'}",
            "",
            f"{self.t('detail_path')}{c}",
            rec.path,
            "",
            f"{self.t('detail_description')}{c}",
            rec.description or "-",
            "",
            f"{self.t('detail_evidence')}{c}",
        ]
        lines += ["  - " + e for e in rec.evidence] if rec.evidence else ["  - " + self.t("none")]
        self.details.setPlainText("\n".join(lines))


    def steam_bridge_exe(self) -> Path:
        return self.steam_bridge_dir() / "steam_ugc_bridge.exe"

    def steam_bridge_dir(self) -> Path:
        return self.user_data / "steam_bridge"

    def steam_bridge_source_dirs(self) -> list[Path]:
        # 中文：按可写运行目录、exe 旁边、打包资源目录、源码目录的顺序查找 Steam 桥接组件。
        # English: Search Steam bridge files from writable runtime dir, exe folder, bundled resources, then source folder.
        dirs = [
            self.steam_bridge_dir(),
            self.base / "steam_bridge",
            self.resource_base / "steam_bridge",
            Path(__file__).resolve().parent / "steam_bridge",
        ]
        clean: list[Path] = []
        seen = set()
        for d in dirs:
            try:
                key = str(d.resolve()).lower()
            except Exception:
                key = str(d).lower()
            if key not in seen:
                seen.add(key)
                clean.append(d)
        return clean

    def steam_api64_candidates(self) -> list[Path]:
        candidates: list[Path] = []
        for bridge in self.steam_bridge_source_dirs():
            candidates.append(bridge / "steam_api64.dll")
        candidates.append(self.base / "steam_api64.dll")
        candidates.append(self.resource_base / "steam_api64.dll")
        roots: list[Path] = []
        if self.l4d2:
            roots += [self.l4d2, self.l4d2.parent]
        try:
            root = self.get_l4d2(silent=True)
            if root:
                roots += [root, root.parent]
        except Exception:
            pass
        for lib in find_steam_libraries():
            roots.append(lib)
            roots.append(lib / "steamapps" / "common" / "Left 4 Dead 2")
        for root in roots:
            if not root:
                continue
            candidates += [
                root / "steam_api64.dll",
                root / "bin" / "steam_api64.dll",
                root / "sdk" / "redistributable_bin" / "win64" / "steam_api64.dll",
                root / "steamapps" / "common" / "Steamworks Shared" / "_CommonRedist" / "Steamworks SDK" / "Redist" / "steam_api64.dll",
            ]
            common = root / "steamapps" / "common"
            if common.exists():
                try:
                    for game_dir in common.iterdir():
                        if not game_dir.is_dir():
                            continue
                        candidates += [
                            game_dir / "steam_api64.dll",
                            game_dir / "bin" / "steam_api64.dll",
                            game_dir / "bin" / "win64" / "steam_api64.dll",
                            game_dir / "bin" / "x64" / "steam_api64.dll",
                        ]
                        try:
                            candidates.extend(game_dir.glob("*_Data/Plugins/x86_64/steam_api64.dll"))
                            candidates.extend(game_dir.glob("Engine/Binaries/ThirdParty/Steamworks/*/Win64/steam_api64.dll"))
                        except Exception:
                            pass
                except Exception:
                    pass
        clean: list[Path] = []
        seen = set()
        for p in candidates:
            key = str(p).lower()
            if key not in seen:
                seen.add(key)
                clean.append(p)
        return clean

    def ensure_steam_integration(self, silent: bool = True) -> dict:
        folder = Path(self.ensure_steam_bridge_scaffold())
        result = {"ready": False, "dll": "", "message": "", "checked": []}
        if os.name != "nt":
            result["message"] = "Windows only"
            return result
        selected = None
        for p in self.steam_api64_candidates():
            try:
                result["checked"].append(str(p))
                if p.exists() and p.is_file():
                    selected = p
                    break
            except Exception:
                pass
        if selected:
            try:
                target = folder / "steam_api64.dll"
                if selected.resolve() != target.resolve():
                    shutil.copy2(selected, target)
                    selected = target
                # 中文：确保 AppID 文件和 DLL 在同一工作目录，避免 SteamAPI_Init 一直失败。
                # English: Keep the AppID file beside the DLL so SteamAPI_Init can resolve the app while running outside Steam.
                (folder / "steam_appid.txt").write_text(L4D2_APP_ID, encoding="utf-8")
            except Exception as exc:
                result["message"] = f"Steam API copy failed: {exc}"
                return result
            result.update({"ready": True, "dll": str(selected), "message": self.t("runtime_status_steam_bridge_ok")})
            return result
        result["message"] = self.t("steam_missing_api")
        return result

    def is_steam_running(self) -> bool:
        try:
            if sys.platform.startswith("win"):
                proc = subprocess.run(["tasklist", "/FI", "IMAGENAME eq steam.exe"], capture_output=True, text=True, errors="ignore", timeout=3, creationflags=self._subprocess_no_window_flags(), startupinfo=self._subprocess_startupinfo())
                return "steam.exe" in (proc.stdout or "").lower()
            proc = subprocess.run(["pgrep", "-f", "steam"], capture_output=True, text=True, errors="ignore", timeout=3)
            return bool((proc.stdout or "").strip())
        except Exception:
            return False

    def update_steam_status_label(self):
        if not hasattr(self, "steam_status_label"):
            return
        self.steam_status_label.setText(self.t("steam_status_connected") if self.is_steam_running() else self.t("steam_status_not_running"))

    def connect_steam_client(self):
        try:
            os.startfile("steam://open/main")
        except Exception:
            try:
                for lib in find_steam_libraries():
                    exe = lib / "steam.exe"
                    if exe.exists():
                        subprocess.Popen([str(exe)], creationflags=self._subprocess_no_window_flags(), startupinfo=self._subprocess_startupinfo())
                        break
            except Exception:
                pass
        QTimer.singleShot(900, self.update_steam_status_label)

    def _load_steam_ugc(self) -> tuple[bool, str, object, int]:
        info = self.ensure_steam_integration(silent=True)
        if not info.get("ready"):
            return False, info.get("message") or self.t("steam_missing_api"), None, 0
        if not self.is_steam_running():
            self.connect_steam_client()
            deadline = time.time() + 8.0
            while time.time() < deadline and not self.is_steam_running():
                QApplication.processEvents()
                time.sleep(0.25)
        try:
            import ctypes
            dll_path = str(info.get("dll"))
            dll_dir = str(Path(dll_path).parent)
            try:
                os.add_dll_directory(dll_dir)
            except Exception:
                pass
            os.environ.setdefault("SteamAppId", L4D2_APP_ID)
            os.environ.setdefault("SteamGameId", L4D2_APP_ID)
            old_cwd = os.getcwd()
            try:
                os.chdir(dll_dir)
            except Exception:
                old_cwd = None
            try:
                dll = ctypes.WinDLL(dll_path)
                init_ok = False
                init_error = ""
                try:
                    init = getattr(dll, "SteamAPI_Init")
                    init.restype = ctypes.c_bool
                    init_ok = bool(init())
                except AttributeError:
                    pass
                if not init_ok:
                    try:
                        init_safe = getattr(dll, "SteamAPI_InitSafe")
                        init_safe.restype = ctypes.c_bool
                        init_ok = bool(init_safe())
                    except AttributeError:
                        pass
                if not init_ok:
                    try:
                        init_flat = getattr(dll, "SteamAPI_InitFlat")
                        init_flat.argtypes = [ctypes.c_void_p]
                        init_flat.restype = ctypes.c_int
                        err_buf = ctypes.create_string_buffer(1024)
                        result = int(init_flat(ctypes.byref(err_buf)))
                        init_ok = (result == 0)
                        init_error = (err_buf.value or b"").decode("utf-8", errors="ignore").strip()
                    except AttributeError:
                        init_error = "Steam API init export not found"
                if not init_ok:
                    return False, (init_error or self.t("steam_init_failed")), None, 0
                ugc = 0
                for ver in range(25, 12, -1):
                    name = f"SteamAPI_SteamUGC_v{ver:03d}"
                    try:
                        fn = getattr(dll, name)
                        fn.restype = ctypes.c_void_p
                        ptr = fn()
                        if ptr:
                            ugc = int(ptr)
                            break
                    except Exception:
                        continue
                if not ugc:
                    try:
                        shutdown = getattr(dll, "SteamAPI_Shutdown")
                        shutdown()
                    except Exception:
                        pass
                    return False, self.t("steam_ugc_failed"), None, 0
                return True, "", dll, ugc
            finally:
                if old_cwd:
                    try:
                        os.chdir(old_cwd)
                    except Exception:
                        pass
        except Exception as exc:
            return False, str(exc), None, 0

    def _shutdown_steam_api_after_ugc(self, dll=None):
        try:
            target = dll or getattr(self, "_steam_api_dll", None)
            if target is not None:
                try:
                    shutdown = getattr(target, "SteamAPI_Shutdown")
                    shutdown()
                except Exception:
                    pass
        finally:
            try:
                self._steam_api_dll = None
                self._steam_ugc_ptr = 0
            except Exception:
                pass

    def steam_ugc_action(self, action: str, ids: list[str]) -> tuple[bool, str]:
        clean_ids = []
        for wid in ids:
            s = str(wid).strip()
            if s.isdigit() and s not in clean_ids:
                clean_ids.append(s)
        if not clean_ids:
            return False, self.t("workshop_no_id")
        ok, msg, dll, ugc = self._load_steam_ugc()
        if not ok:
            return False, msg
        try:
            import ctypes
            if action == "subscribe":
                flat_name = "SteamAPI_ISteamUGC_SubscribeItem"
                vtable_index = 72
                done_key = "workshop_subscribe_done"
            elif action == "unsubscribe":
                flat_name = "SteamAPI_ISteamUGC_UnsubscribeItem"
                vtable_index = 73
                done_key = "workshop_unsubscribe_done"
            else:
                return False, action

            used_path = ""
            try:
                fn = getattr(dll, flat_name)
                fn.argtypes = [ctypes.c_void_p, ctypes.c_ulonglong]
                fn.restype = ctypes.c_ulonglong
                for wid in clean_ids:
                    fn(ctypes.c_void_p(ugc), ctypes.c_ulonglong(int(wid)))
                used_path = "flat"
            except AttributeError:
                ptr_size = ctypes.sizeof(ctypes.c_void_p)
                vtable_ptr = ctypes.cast(ctypes.c_void_p(ugc), ctypes.POINTER(ctypes.c_void_p))[0]
                method_addr = ctypes.cast(
                    ctypes.c_void_p(vtable_ptr + vtable_index * ptr_size),
                    ctypes.POINTER(ctypes.c_void_p)
                )[0]
                if not method_addr:
                    return False, f"Steam UGC 函数不可用：{flat_name}"
                call_type = getattr(ctypes, "WINFUNCTYPE", ctypes.CFUNCTYPE)
                method = call_type(ctypes.c_ulonglong, ctypes.c_void_p, ctypes.c_ulonglong)(method_addr)
                for wid in clean_ids:
                    method(ctypes.c_void_p(ugc), ctypes.c_ulonglong(int(wid)))
                used_path = "vtable"

            try:
                run_cb = getattr(dll, "SteamAPI_RunCallbacks")
                for _ in range(18):
                    run_cb()
                    QApplication.processEvents()
                    time.sleep(0.035)
            except Exception:
                pass
            return True, self.t(done_key, n=len(clean_ids))
        except Exception as exc:
            return False, str(exc)
        finally:
            self._shutdown_steam_api_after_ugc(dll)

    def run_steam_bridge(self, action: str, ids: list[str]) -> tuple[bool, str]:
        return self.steam_ugc_action(action, ids)

    def steam_unsubscribe_selected_workshop_items(self):
        recs = self.selected_workshop_records()
        if not recs:
            QMessageBox.information(self, APP_NAME, self.t("workshop_no_id"))
            return
        self.save_workshop_unsubscribe_history(recs)
        ids = [str(r.workshop_id) for r in recs]
        ok, msg = self.run_steam_bridge("unsubscribe", ids)
        if ok:
            QMessageBox.information(self, APP_NAME, msg or self.t("workshop_unsubscribe_done", n=len(recs)))
            QTimer.singleShot(1200, self.scan)
        else:
            QMessageBox.warning(self, APP_NAME, self.t("steam_direct_failed", reason=msg))
        self.update_steam_status_label()

    def save_workshop_unsubscribe_history(self, recs: list[ModRecord]):
        history = self.load_workshop_history()
        by_id = {str(x.get("id")): x for x in history}
        now = time.strftime("%Y-%m-%d %H:%M:%S")
        for rec in recs:
            by_id[str(rec.workshop_id)] = {
                "id": str(rec.workshop_id),
                "title": rec.title,
                "path": rec.path,
                "time": now,
                "url": self.workshop_item_url(rec.workshop_id),
            }
        self.save_workshop_history(list(by_id.values()))

    def workshop_history_path(self) -> Path:
        return self.base / "danyria_workshop_unsubscribe_history.json"

    def load_workshop_history(self) -> list[dict]:
        try:
            data = json.loads(self.workshop_history_path().read_text(encoding="utf-8"))
            if isinstance(data, list):
                return [x for x in data if isinstance(x, dict) and str(x.get("id", "")).isdigit()]
        except Exception:
            pass
        return []

    def save_workshop_history(self, items: list[dict]):
        try:
            self.workshop_history_path().write_text(json.dumps(items, ensure_ascii=False, indent=2), encoding="utf-8")
        except Exception:
            pass

    def merge_workshop_manifest_records(self, root: Path, records: list[ModRecord]) -> list[ModRecord]:
        manifest = read_l4d2_workshop_manifest(root)
        if not manifest:
            return records
        by_id = {r.workshop_id: r for r in records if r.source == "Workshop" and r.workshop_id}
        workshop_folder = root / "addons" / "workshop"
        for wid, meta in manifest.items():
            if not wid.isdigit():
                continue
            local_candidates = []
            local_candidates.append(workshop_folder / f"{wid}.vpk")
            local_candidates.append(workshop_folder / f"{wid}.vpk.disabled")
            local_candidates.append(workshop_folder / wid)
            content_path = workshop_content_path_for_id(root, wid)
            if content_path:
                local_candidates.append(content_path)
            existing = by_id.get(wid)
            note = "synced from Steam appworkshop_550.acf"
            if existing:
                if note not in existing.evidence:
                    existing.evidence.insert(0, note)
                continue
            found = next((p for p in local_candidates if p.exists()), None)
            size = folder_size_mb(found) if found and found.is_dir() else (file_size_mb(found) if found else 0.0)
            status = "Subscribed" if found else "Missing"
            modified = modified_str(found) if found else ""
            path = str(found if found else (workshop_folder / f"{wid}.vpk"))
            evidence = [note]
            if content_path:
                evidence.append(f"Steam content folder: {content_path}")
            if not found:
                evidence.append("local workshop VPK/folder is missing; Steam may redownload it while subscribed")
            title = meta.get("title") or f"Workshop {wid}"
            records.append(ModRecord(title, "Unknown", "Workshop", "Workshop", status, path, size, "", "", modified, ["workshop"], evidence, True, wid))
        return records

    def sync_workshop_items(self):
        self.scan()
        n = len([r for r in self.records if r.source == "Workshop"])
        QMessageBox.information(self, APP_NAME, self.t("workshop_sync_done", n=n))

    def workshop_item_url(self, wid: str) -> str:
        return f"https://steamcommunity.com/sharedfiles/filedetails/?id={wid}"

    def open_steam_url(self, url: str):
        try:
            os.startfile("steam://openurl/" + url)
            return True
        except Exception:
            try:
                webbrowser.open(url)
                return True
            except Exception:
                return False

    def open_workshop_item_page(self, wid: str):
        return self.open_steam_url(self.workshop_item_url(str(wid)))

    def selected_workshop_records(self) -> list[ModRecord]:
        return [r for r in self.selected_records() if r.source == "Workshop" and str(r.workshop_id).isdigit()]

    def open_selected_workshop_pages(self):
        recs = self.selected_workshop_records()
        if not recs:
            self.open_steam_url(f"https://steamcommunity.com/workshop/browse/?appid={L4D2_APP_ID}")
            return
        for rec in recs[:12]:
            self.open_workshop_item_page(rec.workshop_id)


    def unsubscribe_selected_workshop_items(self):
        return self.steam_unsubscribe_selected_workshop_items()

    def open_workshop_history_dialog(self):
        history = self.load_workshop_history()
        if not history:
            QMessageBox.information(self, self.t("workshop_history_title"), self.t("workshop_history_empty"))
            return
        dlg = QDialog(self)
        dlg.setWindowTitle(self.t("workshop_history_title"))
        dlg.resize(760, 420)
        lay = QVBoxLayout(dlg)
        hint = QLabel(self.t("workshop_history_restore_tip"))
        hint.setWordWrap(True)
        hint.setObjectName("TinyText")
        lay.addWidget(hint)
        table = QTableWidget(0, 4)
        table.setHorizontalHeaderLabels(["ID", self.t("detail_name"), self.t("detail_modified"), self.t("detail_path")])
        table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        table.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        for row, item in enumerate(sorted(history, key=lambda x: str(x.get("time", "")), reverse=True)):
            table.insertRow(row)
            for col, val in enumerate([item.get("id", ""), item.get("title", ""), item.get("time", ""), item.get("path", "")]):
                cell = QTableWidgetItem(str(val))
                cell.setData(Qt.ItemDataRole.UserRole, item.get("id", ""))
                table.setItem(row, col, cell)
        lay.addWidget(table, 1)
        buttons = QHBoxLayout()
        open_btn = QPushButton(self.t("workshop_history_open_selected"))
        restore_btn = QPushButton(self.t("workshop_history_subscribe_selected"))
        forget_btn = QPushButton(self.t("workshop_history_forget_selected"))
        clear_btn = QPushButton(self.t("workshop_history_clear"))
        close_btn = QPushButton(self.t("workshop_history_close"))
        buttons.addWidget(open_btn)
        buttons.addWidget(restore_btn)
        buttons.addWidget(forget_btn)
        buttons.addWidget(clear_btn)
        buttons.addStretch(1)
        buttons.addWidget(close_btn)
        lay.addLayout(buttons)

        def selected_ids():
            ids = []
            try:
                rows = sorted({idx.row() for idx in table.selectionModel().selectedRows()})
            except Exception:
                rows = []
            for row in rows:
                cell = table.item(row, 0)
                if cell:
                    ids.append(str(cell.text()))
            return ids

        def open_selected():
            ids = selected_ids() or [str(history[0].get("id"))]
            for wid in ids[:12]:
                if wid.isdigit():
                    self.open_workshop_item_page(wid)

        def forget_selected():
            ids = set(selected_ids())
            if not ids:
                return
            new_history = [x for x in self.load_workshop_history() if str(x.get("id")) not in ids]
            self.save_workshop_history(new_history)
            for row in reversed(range(table.rowCount())):
                cell = table.item(row, 0)
                if cell and cell.text() in ids:
                    table.removeRow(row)

        def restore_selected():
            ids = selected_ids() or [str(history[0].get("id"))]
            ok, msg = self.run_steam_bridge("subscribe", ids[:24])
            if ok:
                QMessageBox.information(self, APP_NAME, msg or self.t("workshop_subscribe_done", n=len(ids[:24])))
                QTimer.singleShot(1200, self.scan)
            else:
                QMessageBox.warning(self, APP_NAME, self.t("steam_direct_failed", reason=msg))


        def clear_history():
            self.save_workshop_history([])
            table.setRowCount(0)

        open_btn.clicked.connect(open_selected)
        restore_btn.clicked.connect(restore_selected)
        forget_btn.clicked.connect(forget_selected)
        clear_btn.clicked.connect(clear_history)
        close_btn.clicked.connect(dlg.accept)
        dlg.exec()

    def open_path(self, p: Path):
        try:
            if p.is_file():
                subprocess.Popen(["explorer", "/select,", str(p)])
            else:
                os.startfile(str(p))
        except Exception as exc:
            QMessageBox.warning(self, self.t("open_failed"), str(exc))

    def open_selected(self):
        rec = self.selected()
        if rec:
            p = Path(rec.path)
            if rec.source == "Workshop" and rec.workshop_id and not p.exists():
                self.open_workshop_item_page(rec.workshop_id)
            else:
                self.open_path(p)

    def open_game_dir(self):
        root = self.get_l4d2()
        if root:
            game_dir = root.parent if (root.parent / "left4dead2.exe").exists() else root
            self.open_path(game_dir)

    def open_addons(self):
        root = self.get_l4d2()
        if root:
            self.open_path(root / "addons")

    def open_workshop(self):
        root = self.get_l4d2()
        if root:
            p = root / "addons" / "workshop"
            p.mkdir(parents=True, exist_ok=True)
            self.open_path(p)

    def open_ems(self):
        root = self.get_l4d2()
        if root:
            p = root / "ems"
            p.mkdir(parents=True, exist_ok=True)
            self.open_path(p)

    def _toggle_one_record(self, rec: ModRecord, root: Path) -> tuple[bool, str]:
        p = Path(rec.path)
        if rec.source == "Workshop" and rec.kind == "Workshop":
            return False, f"{rec.title}: {self.t('workshop_manage_hint')}"
        if not p.exists():
            return False, f"{rec.title}: {self.t('not_exists')}"

        if rec.kind == "VPK":
            if rec.status == "Enabled":
                target = p.with_name(p.name + ".disabled")
            else:
                name = p.name[:-9] if p.name.lower().endswith(".disabled") else p.name
                target = p.with_name(name)
        else:
            stash = root / "addons" / "_danyria_disabled"
            stash.mkdir(parents=True, exist_ok=True)
            if rec.status == "Enabled":
                target = stash / p.name
            else:
                target = root / "addons" / p.name

        if target.exists():
            return False, self.t("target_exists", path=target)

        p.rename(target)
        return True, rec.title

    def toggle_selected(self):
        recs = self.selected_records()
        if not recs:
            QMessageBox.information(self, APP_NAME, self.t("select_first"))
            return
        try:
            root = self.get_l4d2()
            if not root:
                return
            workshop_recs = [rec for rec in recs if self.is_workshop_record(rec)]
            if workshop_recs:
                QMessageBox.warning(self, APP_NAME, self.t("workshop_toggle_blocked"))
                return
            ok = 0
            errors = []
            for rec in recs:
                success, message = self._toggle_one_record(rec, root)
                if success:
                    ok += 1
                else:
                    errors.append(message)
            self.scan()
            if errors:
                QMessageBox.warning(self, self.t("operation_failed"), "\n".join(errors[:8]))
            elif ok > 1:
                QMessageBox.information(self, APP_NAME, self.t("batch_toggle_done", n=ok))
        except Exception as exc:
            QMessageBox.warning(self, self.t("operation_failed"), str(exc))

    def unique_addon_path(self, dest_dir: Path, filename: str) -> Path:
        dest = dest_dir / filename
        if not dest.exists():
            return dest
        stem = Path(filename).stem
        suffix = Path(filename).suffix
        stamp = time.strftime("%Y%m%d_%H%M%S")
        return dest_dir / f"{stem}_{stamp}{suffix}"

    def install_vpk_files(self, files: list[Path]):
        root = self.get_l4d2()
        if not root:
            return

        addons = root / "addons"
        addons.mkdir(parents=True, exist_ok=True)

        installed = []
        skipped = []
        for f in files:
            if not f.exists() or not f.is_file():
                skipped.append(str(f))
                continue
            if f.suffix.lower() != ".vpk":
                skipped.append(str(f))
                continue

            dest = self.unique_addon_path(addons, f.name)
            try:
                shutil.copy2(f, dest)
                installed.append(dest.name)
            except Exception as exc:
                QMessageBox.warning(self, self.t("install_failed"), f"{f}\n\n{exc}")
                return

        if installed:
            QMessageBox.information(self, self.t("vpk_installed_title"), self.t("vpk_installed_body", items="\n".join(installed)))
            self.scan()
        elif skipped:
            QMessageBox.information(self, self.t("nothing_installed_title"), self.t("nothing_installed_body"))

    def dragEnterEvent(self, event):
        md = event.mimeData()
        if md.hasUrls():
            for url in md.urls():
                if url.isLocalFile() and Path(url.toLocalFile()).suffix.lower() == ".vpk":
                    event.acceptProposedAction()
                    return
        event.ignore()

    def dropEvent(self, event):
        files = []
        md = event.mimeData()
        if md.hasUrls():
            for url in md.urls():
                if url.isLocalFile():
                    p = Path(url.toLocalFile())
                    if p.suffix.lower() == ".vpk":
                        files.append(p)
        if files:
            try:
                if hasattr(self, "main_stack") and self.main_stack.currentWidget() is getattr(self, "weapons_page", None):
                    self.extract_weapon_scripts_from_vpks(files)
                else:
                    self.install_vpk_files(files)
            except Exception as exc:
                QMessageBox.warning(self, self.t("operation_failed"), str(exc))
            event.acceptProposedAction()
        else:
            event.ignore()

    def launch_game(self):
        try:
            os.startfile("steam://rungameid/550")
            return
        except Exception:
            pass

        root = self.get_l4d2()
        if root:
            exe = root.parent / "left4dead2.exe"
            if exe.exists():
                try:
                    subprocess.Popen([str(exe)], cwd=str(exe.parent))
                    return
                except Exception as exc:
                    QMessageBox.warning(self, self.t("launch_failed"), str(exc))
                    return

        QMessageBox.warning(self, self.t("launch_failed"), self.t("launch_failed_body"))

    def find_vpk_exe(self, root: Path) -> Optional[Path]:
        candidates = [
            root.parent / "bin" / "vpk.exe",
            root.parent / "left4dead2" / "bin" / "vpk.exe",
            root / "bin" / "vpk.exe",
        ]
        for p in candidates:
            if p.exists():
                return p
        return None

    def backup_existing_path(self, p: Path):
        if p.exists():
            backup_root = p.parent / "_danyria_backups"
            backup_root.mkdir(parents=True, exist_ok=True)
            backup = backup_root / (p.name + ".backup_" + time.strftime("%Y%m%d_%H%M%S"))
            p.rename(backup)

    def plugin_install_paths(self, plugin_name: str) -> list[Path]:
        root = self.get_l4d2(silent=True)
        if not root:
            return []
        addons = root / "addons"
        return [
            addons / plugin_name,
            addons / f"{plugin_name}.vpk",
            addons / f"{plugin_name}.vpk.disabled",
            addons / f"{plugin_name}.disabled",
            addons / "_danyria_disabled" / plugin_name,
            addons / "_danyria_disabled" / f"{plugin_name}.vpk",
            addons / "_danyria_disabled" / f"{plugin_name}.vpk.disabled",
        ]

    def remove_plugin_path(self, p: Path):
        if not p.exists():
            return False
        if p.is_dir():
            shutil.rmtree(p)
        else:
            p.unlink()
        return True

    def backup_existing_plugin(self, plugin_name: str):
        for p in self.plugin_install_paths(plugin_name):
            if p.exists():
                self.backup_existing_path(p)

    def delete_plugin_install(self, plugin_name: str, success_key: str, missing_key: str, failed_key: str, refresh_cb=None):
        root = self.get_l4d2()
        if not root:
            return
        try:
            removed = []
            for p in self.plugin_install_paths(plugin_name):
                if self.remove_plugin_path(p):
                    removed.append(p.name)
            if removed:
                QMessageBox.information(self, APP_NAME, self.t(success_key, n=len(removed)))
            else:
                QMessageBox.information(self, APP_NAME, self.t(missing_key))
            self.scan()
            if refresh_cb:
                refresh_cb()
        except Exception as exc:
            QMessageBox.warning(self, self.t(failed_key), str(exc))

    def install_hud_plugin(self):
        root = self.get_l4d2()
        if not root:
            return

        src = self.payload / "danyria_hud_plugin"
        if not src.exists():
            QMessageBox.warning(self, self.t("missing_file"), self.t("missing_hud_plugin_payload"))
            return

        addons = root / "addons"
        addons.mkdir(parents=True, exist_ok=True)
        dest_folder = addons / "danyria_hud_plugin"

        try:
            self.backup_existing_plugin("danyria_hud_plugin")
            generated = src.with_suffix(".vpk")
            if generated.exists():
                generated.unlink()
            shutil.copytree(src, dest_folder)
            QMessageBox.information(self, APP_NAME, self.t("hud_plugin_install_folder_success"))
            self.scan()
            self.update_hud_plugin_status()

        except Exception as exc:
            QMessageBox.warning(self, self.t("hud_plugin_install_failed"), str(exc))

    def delete_hud_plugin(self):
        self.delete_plugin_install(
            "danyria_hud_plugin",
            "hud_plugin_delete_success",
            "hud_plugin_delete_missing",
            "hud_plugin_delete_failed",
            self.update_hud_plugin_status,
        )

    def install_penalty_plugin(self):
        root = self.get_l4d2()
        if not root:
            return

        src = self.payload / "danyria_penalty_plugin"
        if not src.exists():
            QMessageBox.warning(self, self.t("missing_file"), self.t("missing_penalty_plugin_payload"))
            return

        addons = root / "addons"
        addons.mkdir(parents=True, exist_ok=True)
        dest_folder = addons / "danyria_penalty_plugin"

        try:
            self.backup_existing_plugin("danyria_penalty_plugin")
            generated = src.with_suffix(".vpk")
            if generated.exists():
                generated.unlink()
            shutil.copytree(src, dest_folder)
            try:
                self.write_score_rules(self.collect_score_rules_from_ui())
            except Exception:
                pass
            QMessageBox.information(self, APP_NAME, self.t("penalty_plugin_install_folder_success"))
            self.scan()
            self.update_penalty_plugin_status()
        except Exception as exc:
            QMessageBox.warning(self, self.t("penalty_plugin_install_failed"), str(exc))

    def delete_penalty_plugin(self):
        self.delete_plugin_install(
            "danyria_penalty_plugin",
            "penalty_plugin_delete_success",
            "penalty_plugin_delete_missing",
            "penalty_plugin_delete_failed",
            self.update_penalty_plugin_status,
        )

    def hud_test_launch_command(self) -> list[str]:
        return ["+map", "c1m1_hotel", "danyria_hud"]

    def detect_hud_test_memory_risk(self, root: Path) -> tuple[bool, str]:
        try:
            addons = root / "addons"
            mod_count = 0
            if addons.exists():
                for child in addons.iterdir():
                    low = child.name.lower()
                    if low in ("workshop", "_danyria_disabled", "_danyria_backups"):
                        continue
                    if child.is_file() and not (low.endswith(".vpk") or low.endswith(".vpk.disabled")):
                        continue
                    mod_count += 1
                ws = addons / "workshop"
                if ws.exists():
                    mod_count += sum(1 for p in ws.iterdir() if p.is_file() and p.name.lower().endswith(".vpk"))
            game_dir = root.parent
            dxvk = any((game_dir / name).exists() for name in ("dxgi.dll", "d3d9.dll", "d3d11.dll", "vulkan-1.dll"))
            l4n = False
            try:
                hay_dirs = [root / "addons", root / "addons" / "workshop"]
                for d in hay_dirs:
                    if not d.exists():
                        continue
                    for child in list(d.iterdir())[:600]:
                        low = child.name.lower()
                        if "left4neko" in low or "l4n" in low or "neko" in low:
                            l4n = True
                            break
                    if l4n:
                        break
            except Exception:
                pass
            risky = mod_count >= 160 or (mod_count >= 80 and (dxvk or l4n))
            detail = f"MOD={mod_count}, DXVK={'yes' if dxvk else 'no'}, L4N={'yes' if l4n else 'no'}"
            return risky, detail
        except Exception:
            return False, ""

    def confirm_hud_test_launch(self, root: Path) -> bool:
        risky, detail = self.detect_hud_test_memory_risk(root)
        if not risky:
            return True
        command = "map c1m1_hotel danyria_hud"
        try:
            QApplication.clipboard().setText(command)
        except Exception:
            pass
        msg = self.t("hud_test_memory_warning", detail=detail, command=command)
        return QMessageBox.question(self, self.t("launch_hud_test_campaign"), msg) == QMessageBox.StandardButton.Yes

    def launch_penalty_test_campaign(self):
        root = self.get_l4d2()
        if not root:
            return

        self.launch_hud()
        if not self.confirm_hud_test_launch(root):
            return

        exe = root.parent / "left4dead2.exe"
        if not exe.exists():
            QMessageBox.warning(self, self.t("launch_penalty_test_failed"), self.t("launch_hud_test_missing_exe"))
            return

        try:
            subprocess.Popen(
                [str(exe)] + self.hud_test_launch_command(),
                cwd=str(exe.parent)
            )
        except Exception as exc:
            QMessageBox.warning(self, self.t("launch_penalty_test_failed"), str(exc))

    def launch_hud_test_campaign(self):
        root = self.get_l4d2()
        if not root:
            return

        self.launch_hud()
        if not self.confirm_hud_test_launch(root):
            return

        exe = root.parent / "left4dead2.exe"
        if not exe.exists():
            QMessageBox.warning(self, self.t("launch_hud_test_failed"), self.t("launch_hud_test_missing_exe"))
            return

        try:
            subprocess.Popen(
                [str(exe)] + self.hud_test_launch_command(),
                cwd=str(exe.parent)
            )
        except Exception as exc:
            QMessageBox.warning(self, self.t("launch_hud_test_failed"), str(exc))


    def stop_hud_process(self):
        proc = getattr(self, "hud_process", None)
        if not proc:
            return
        try:
            if proc.poll() is None:
                proc.terminate()
                try:
                    proc.wait(timeout=1.5)
                except Exception:
                    proc.kill()
        except Exception:
            pass
        self.hud_process = None

    def launch_hud(self, show_errors: bool = True):
        root = self.get_l4d2(silent=not show_errors)
        hud = self.hud_script_path()
        hud_exe = self.hud_exe_path()
        if not hud and not hud_exe and not getattr(sys, "frozen", False):
            if show_errors:
                QMessageBox.warning(self, self.t("missing_hud"), self.t("missing_hud_body"))
            return

        self.sync_hud_language_config()
        self.stop_hud_process()

        env = os.environ.copy()
        try:
            env["DANYRIA_HUD_CONFIG"] = str(self.hud_config_path())
        except Exception:
            pass

        commands = []
        if hud_exe:
            cmd = [str(hud_exe)]
            if root:
                cmd.append(str(root))
            commands.append((cmd, hud_exe.parent))
        if getattr(sys, "frozen", False):
            cmd = [str(sys.executable), "--danyria-hud"]
            if root:
                cmd.append(str(root))
            commands.append((cmd, self.base))
        if hud:
            for pycmd in self.hud_python_launch_candidates():
                cmd = list(pycmd) + [str(hud)]
                if root:
                    cmd.append(str(root))
                commands.append((cmd, hud.parent))

        last_error = ""
        for cmd, cwd in commands:
            try:
                self.hud_process = subprocess.Popen(
                    cmd,
                    cwd=str(cwd),
                    env=env,
                    creationflags=self._subprocess_no_window_flags(),
                    startupinfo=self._subprocess_startupinfo(),
                )
                self.append_runtime_log("HUD launch command: " + " ".join(cmd))
                return
            except FileNotFoundError as exc:
                last_error = str(exc)
            except Exception as exc:
                last_error = str(exc)

        self.append_runtime_log("HUD launch failed: " + last_error)
        if show_errors:
            QMessageBox.warning(self, self.t("python_not_found"), self.t("python_not_found_body") + "\n\nHUD: " + last_error)

    def closeEvent(self, event):
        self.stop_hud_process()
        try:
            QApplication.instance().removeEventFilter(self)
        except Exception:
            pass
        super().closeEvent(event)

def main():
    import sys
    app = QApplication(sys.argv)
    icon = first_existing_dir("assets") / "avatar_normal.png"
    if not icon.exists():
        icon = first_existing_dir("assets") / "avatar.png"
    if icon.exists():
        app.setWindowIcon(QIcon(str(icon)))
    w = DanyriaWindow()
    w.show()
    sys.exit(app.exec())

def run_embedded_hud(self_test: bool = False):
    candidates = [
        first_existing_dir("payload", "danyria_hud", "DanyriaHUD.pyw"),
        resource_dir() / "payload" / "danyria_hud" / "DanyriaHUD.pyw",
        base_dir() / "payload" / "danyria_hud" / "DanyriaHUD.pyw",
    ]
    hud = next((p for p in candidates if p.exists()), None)
    if not hud:
        print("Danyria HUD script was not found.", file=sys.stderr)
        return 2
    args = [str(hud)]
    if self_test:
        args.append("--self-test")
    else:
        args.extend([a for a in sys.argv[2:] if a != "--danyria-hud"])
    sys.argv = args
    runpy.run_path(str(hud), run_name="__main__")
    return 0

if __name__ == "__main__":
    try:
        if "--danyria-hud-self-test" in sys.argv:
            sys.exit(run_embedded_hud(self_test=True))
        if "--danyria-hud" in sys.argv:
            sys.exit(run_embedded_hud(self_test=False))
        main()
    except Exception as exc:
        import traceback
        log_path = base_dir() / "danyria_crash_log.txt"
        try:
            log_path.write_text(traceback.format_exc(), encoding="utf-8", errors="replace")
        except Exception:
            pass
        try:
            import ctypes
            ctypes.windll.user32.MessageBoxW(
                None,
                f"Danyria 启动失败。错误日志已写入：\n{log_path}\n\n{exc}",
                "Danyria Crash",
                0x10
            )
        except Exception:
            pass
        raise
