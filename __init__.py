#dev by mizmu.
#Part of this addon from addon 1024346707 by Arthur Milchior
#Support my development by Buy Me Coffee - https://www.buymeacoffee.com/jhhomshl

from typing import Optional
import aqt
from anki.collection import OpChangesWithId
from anki.decks import DeckId
from anki.hooks import wrap
from anki.lang import _
from aqt import mw, gui_hooks, AnkiQt
from aqt.operations import CollectionOp

from aqt.operations.deck import add_deck
from aqt.operations.scheduling import rebuild_filtered_deck, empty_filtered_deck
from aqt.overview import Overview
from aqt.qt import *
from aqt.utils import getOnlyText, tr


def _showOptionsadd(self, did: str, _old) -> None:
    deck = aqt.mw.col.decks.get(did)
    m = QMenu(self.mw)
    a = m.addAction(tr.actions_rename())
    qconnect(a.triggered, lambda b, did=did: self._rename(DeckId(int(did))))
    a = m.addAction(tr.actions_options())
    qconnect(a.triggered, lambda b, did=did: self._options(DeckId(int(did))))
    a = m.addAction(tr.actions_export())
    qconnect(a.triggered, lambda b, did=did: self._export(DeckId(int(did))))
    a = m.addAction(tr.actions_delete())
    a.triggered.connect(lambda b, did=did: open_window(DeckId(int(did))))
    m.addSeparator()
    if deck["dyn"] == False:
        a = m.addAction(_("Create Sub Deck"))
        a.triggered.connect(lambda b, did=did: _on_create(DeckId(int(did))))
    m.addSeparator()
    a = m.addAction(_("Review"))
    a.triggered.connect(lambda b, did=did: _reviewDeck(DeckId(int(did))))
    a = m.addAction(_("Overview"))
    a.triggered.connect(lambda b, did=did: _overviewDeck(DeckId(int(did))))
    if deck["dyn"] == False:
        a = m.addAction(_("Add Card..."))
        a.triggered.connect(lambda b, did=did: AddCard(DeckId(int(did))))
    a = m.addAction(_('Browse...'))
    a.triggered.connect(lambda b, did=did: inBrowser(DeckId(int(did))))
    gui_hooks.deck_browser_will_show_options_menu(m, int(did))

    m.addSeparator()
    #     if node.filtered:
    if deck["dyn"]:
        a = m.addAction(_("Rebuild"))
        a.triggered.connect(lambda b : rebuild_current_filtered_deck(self, DeckId(int(did))))
        a = m.addAction(_("Empty"))
        a.triggered.connect(lambda b : empty_current_filtered_deck(self, DeckId(int(did))))
    else:
        a = m.addAction(_("Filter..."))
        a.triggered.connect(lambda b, did=did: createfiiltered(DeckId(int(did))))

    m.exec_(QCursor.pos())

aqt.deckbrowser.DeckBrowser._showOptions = wrap(aqt.deckbrowser.DeckBrowser._showOptions, _showOptionsadd , 'around')

def AddCard(did):
    mw.col.decks.select(did)
    mw.onAddCard ()

def createfiiltered(did):
    mw.col.decks.select(did)
    mw.onCram()

def FilteredDeckConfig(self, did):
    mw.col.decks.select(did)
    aqt.overview.Overview.rebuild_current_filtered_deck(self)

def rebuild_current_filtered_deck(self, did) -> None:
    rebuild_filtered_deck(
        parent=mw, deck_id=did
    ).run_in_background()

def empty_current_filtered_deck(self, did) -> None:
        empty_filtered_deck(
            parent=mw, deck_id=did
        ).run_in_background()

def inBrowser(did):
    deck = aqt.mw.col.decks.get(did)
    deckName = deck['name']
    browser = aqt.dialogs.open("Browser", aqt.mw)
    browser.search_for(f"\"deck:{deckName}\"")
    browser.update_history()

class ask_before_delete(QDialog):
    def __init__(self, parent=mw):
        super(ask_before_delete, self).__init__(parent)
        self.setWindowTitle("Remove Deck")
        self.setWindowFlags(Qt.Dialog | Qt.MSWindowsFixedSizeDialogHint)

        self._operator = QComboBox()
        self._explanation = QLabel()
        self._explanation.setWordWrap(True)
        buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)
        layout = QGridLayout()
        layout.addWidget(QLabel('<font color=red>Are you sure you want to delete the Deck?</font>'), 6, 0, 1, 3)
        layout.addWidget(buttonBox, 8, 0, 7, 9)
        self.setLayout(layout)
        return


def open_window(did):
    ask_delete = ask_before_delete()
    if ask_delete.exec():
        aqt.operations.deck.remove_decks(parent=mw, deck_ids=[did]).run_in_background()


def _on_create(did: int) -> None:
    if op := add_sub_deck_dialog(did, parent=mw):
        op.run_in_background()
 
def add_sub_deck_dialog(
    did: int,
    *,
    parent: QWidget,
    default_text: str = "",
) -> Optional[CollectionOp[OpChangesWithId]]:
    deck = aqt.mw.col.decks.get(did)
    deckName = deck['name']
    if name := getOnlyText(
        tr.decks_new_deck_name(), default=default_text, parent=parent
    ).strip():
        return add_deck(parent=parent, name=deckName + "::" + name)
    else:
        return None

def _overviewDeck(did):
    mw.col.decks.select(did)
    mw.realOverview ()

def _reviewDeck(did):
    mw.col.decks.select(did)
    mw.col.startTimebox()
    mw.moveToState("review")

def realOverview(self):
    self.col.reset()
    self.moveToState("overview")

AnkiQt.realOverview = realOverview
