"""
Τζόκερ – Λόττο – ΚΙΝΟ: παραγωγή αριθμών με βάση στατιστικά προηγούμενων κληρώσεων.
"""
import threading

from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.metrics import dp
from kivy.properties import ListProperty, StringProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.stacklayout import StackLayout

import lottery as L

Window.clearcolor = (0.96, 0.96, 0.95, 1)
INK = (0.11, 0.14, 0.2, 1)
GREY = (0.42, 0.45, 0.52, 1)
GAME_COLORS = {"joker": (0.85, 0.2, 0.2, 1), "lotto": (0.1, 0.45, 0.8, 1), "kino": (0.95, 0.6, 0.05, 1)}

KV = """
#:import dp kivy.metrics.dp

<Ball>:
    size_hint: None, None
    size: dp(42), dp(42)
    bold: True
    font_size: '17sp'
    color: 1, 1, 1, 1
    canvas.before:
        Color:
            rgba: self.bg
        Ellipse:
            pos: self.pos
            size: self.size

<Txt@Label>:
    size_hint_y: None
    markup: True
    color: 0.11, 0.14, 0.2, 1
    halign: 'left'
    valign: 'top'
    text_size: self.width - dp(8), None
    height: self.texture_size[1] + dp(6)

<GameBtn@ToggleButton>:
    group: 'game'
    allow_no_selection: False
    bold: True
    background_normal: ''
    background_down: ''
    background_color: (0.11, 0.14, 0.2, 1) if self.state == 'down' else (0.85, 0.86, 0.88, 1)
    color: (1, 1, 1, 1) if self.state == 'down' else (0.11, 0.14, 0.2, 1)

<Root>:
    orientation: 'vertical'
    BoxLayout:
        size_hint_y: None
        height: dp(56)
        padding: dp(12), dp(6)
        canvas.before:
            Color:
                rgba: 0.11, 0.14, 0.2, 1
            Rectangle:
                pos: self.pos
                size: self.size
        Label:
            text: 'Τζόκερ · Λόττο · ΚΙΝΟ'
            bold: True
            font_size: '19sp'
            halign: 'left'
            valign: 'middle'
            text_size: self.size
    BoxLayout:
        size_hint_y: None
        height: dp(50)
        padding: dp(8), dp(6)
        spacing: dp(6)
        GameBtn:
            text: 'ΤΖΟΚΕΡ'
            state: 'down'
            on_release: app.set_game('joker')
        GameBtn:
            text: 'ΛΟΤΤΟ'
            on_release: app.set_game('lotto')
        GameBtn:
            text: 'ΚΙΝΟ'
            on_release: app.set_game('kino')
    ScrollView:
        do_scroll_x: False
        BoxLayout:
            id: body
            orientation: 'vertical'
            size_hint_y: None
            height: self.minimum_height
            padding: dp(14), dp(8)
            spacing: dp(8)
            BoxLayout:
                size_hint_y: None
                height: dp(46)
                spacing: dp(8)
                Label:
                    text: 'Μέθοδος'
                    color: 0.11, 0.14, 0.2, 1
                    size_hint_x: 0.3
                    halign: 'left'
                    text_size: self.size
                    valign: 'middle'
                Spinner:
                    id: method
                    text: 'Ισορροπημένη'
                    values: app.methods
            BoxLayout:
                size_hint_y: None
                height: dp(46)
                spacing: dp(8)
                Label:
                    text: 'Στήλες'
                    color: 0.11, 0.14, 0.2, 1
                    size_hint_x: 0.3
                    halign: 'left'
                    text_size: self.size
                    valign: 'middle'
                Spinner:
                    id: columns
                    text: '3'
                    values: [str(i) for i in range(1, 11)]
            BoxLayout:
                id: kino_row
                size_hint_y: None
                height: dp(46) if app.game == 'kino' else 0
                opacity: 1 if app.game == 'kino' else 0
                disabled: app.game != 'kino'
                spacing: dp(8)
                Label:
                    text: 'Αριθμοί ΚΙΝΟ'
                    color: 0.11, 0.14, 0.2, 1
                    size_hint_x: 0.3
                    halign: 'left'
                    text_size: self.size
                    valign: 'middle'
                Spinner:
                    id: kino_pick
                    text: '6'
                    values: [str(i) for i in range(1, 13)]
            BoxLayout:
                size_hint_y: None
                height: dp(46)
                spacing: dp(8)
                Label:
                    text: 'Ανάλυση κληρώσεων'
                    color: 0.11, 0.14, 0.2, 1
                    size_hint_x: 0.3
                    halign: 'left'
                    text_size: self.size
                    valign: 'middle'
                Spinner:
                    id: depth
                    text: '200'
                    values: ['50', '100', '200', '500']
            BoxLayout:
                size_hint_y: None
                height: dp(46)
                CheckBox:
                    id: avoid
                    active: True
                    size_hint_x: None
                    width: dp(46)
                    color: 0.11, 0.14, 0.2, 1
                Label:
                    text: 'Αποφυγή δημοφιλών συνδυασμών (γενέθλια, σειρές)'
                    color: 0.11, 0.14, 0.2, 1
                    halign: 'left'
                    valign: 'middle'
                    text_size: self.size
            BoxLayout:
                size_hint_y: None
                height: dp(54)
                spacing: dp(8)
                Button:
                    id: upd
                    text: 'ΕΝΗΜΕΡΩΣΗ\\nΚΛΗΡΩΣΕΩΝ'
                    halign: 'center'
                    bold: True
                    background_normal: ''
                    background_color: 0.11, 0.14, 0.2, 1
                    on_release: app.update_history()
                Button:
                    text: 'ΒΓΑΛΕ\\nΑΡΙΘΜΟΥΣ'
                    halign: 'center'
                    bold: True
                    background_normal: ''
                    background_color: 0.95, 0.71, 0.14, 1
                    color: 0.11, 0.14, 0.2, 1
                    on_release: app.make_numbers()
            Txt:
                id: status
                font_size: '13sp'
                color: 0.42, 0.45, 0.52, 1
            BoxLayout:
                id: results
                orientation: 'vertical'
                size_hint_y: None
                height: self.minimum_height
                spacing: dp(10)
            Txt:
                id: stats
"""


class Ball(Label):
    bg = ListProperty([0.1, 0.45, 0.8, 1])


class Root(BoxLayout):
    pass


Builder.load_string(KV)


class TzokerApp(App):
    title = "Tzoker Lotto Kino"
    methods = L.METHODS
    game = StringProperty("joker")

    def build(self):
        L.set_dir(self.user_data_dir)
        self.root_w = Root()
        self.busy = False
        Clock.schedule_once(lambda dt: self.set_game("joker"), 0)
        return self.root_w

    @property
    def ids(self):
        return self.root_w.ids

    def set_game(self, game):
        self.game = game
        self.ids.results.clear_widgets()
        data = L.load(game)
        self._show_info(data)
        if not data["draws"]:
            self.update_history()

    def _show_info(self, data, extra=""):
        g = L.GAMES[self.game]
        draws = data.get("draws") or []
        if draws:
            last = draws[0]
            nums = "  ".join(f"{x:02d}" for x in sorted(last["numbers"][: g["draw"]]))
            b = f"  +  Τζόκερ {last['bonus'][0]:02d}" if self.game == "joker" and last.get("bonus") else ""
            self.ids.status.text = (f"{len(draws)} κληρώσεις στη μνήμη · ενημέρωση {data.get('updated') or '-'}\n"
                                    f"Τελευταία κλήρωση #{last['id']} {last['time']}:  [b]{nums}{b}[/b]" + extra)
            self._show_stats(draws)
        else:
            self.ids.status.text = ("Δεν υπάρχουν ακόμα κληρώσεις. Πάτα «ΕΝΗΜΕΡΩΣΗ ΚΛΗΡΩΣΕΩΝ». "
                                    "Μπορείς να βγάλεις αριθμούς και χωρίς αυτές (εντελώς τυχαία)." + extra)
            self.ids.stats.text = self._footer()

    def _show_stats(self, draws):
        depth = int(self.ids.depth.text)
        st = L.stats(self.game, draws[:depth])
        f, gp = st["freq"], st["gap"]
        hot = ", ".join(f"{k} ({f[k]})" for k in st["hot"][:8])
        cold = ", ".join(f"{k} ({gp[k]})" for k in st["cold"][:8])
        txt = (f"[size=16sp][b]Στατιστικά τελευταίων {st['n']} κληρώσεων[/b][/size]\n"
               f"[b]Πιο συχνοί[/b] (εμφανίσεις): {hot}\n"
               f"[b]Πιο καθυστερημένοι[/b] (κληρώσεις χωρίς να βγουν): {cold}\n")
        if self.game == "joker" and st["bfreq"]:
            bh = sorted(st["bfreq"], key=lambda k: -st["bfreq"][k])[:5]
            txt += "[b]Συχνότεροι Τζόκερ[/b]: " + ", ".join(f"{k} ({st['bfreq'][k]})" for k in bh) + "\n"
        self.ids.stats.text = txt + self._footer()

    def _footer(self):
        pick = int(self.ids.kino_pick.text) if self.game == "kino" else None
        return (f"\n[b]{L.odds_text(self.game, pick)}[/b]\n"
                "[size=12sp][color=#6B7486]Κάθε κλήρωση είναι τυχαία και ανεξάρτητη: τα στατιστικά δεν προβλέπουν την "
                "επόμενη. Η αποφυγή δημοφιλών συνδυασμών δεν αυξάνει την πιθανότητα κέρδους, μειώνει όμως την "
                "πιθανότητα να μοιραστείς το έπαθλο. Παίζε με μέτρο.[/color][/size]")

    # ------------------------------------------------------------ παραγωγή
    def make_numbers(self):
        g = L.GAMES[self.game]
        data = L.load(self.game)
        draws = (data.get("draws") or [])[: int(self.ids.depth.text)]
        method = self.ids.method.text if draws else "Εντελώς τυχαία"
        pick = int(self.ids.kino_pick.text) if self.game == "kino" else None
        cols = L.generate(self.game, draws, method, columns=int(self.ids.columns.text), pick=pick,
                          avoid_popular=self.ids.avoid.active)
        box = self.ids.results
        box.clear_widgets()
        color = GAME_COLORS[self.game]
        for i, c in enumerate(cols, 1):
            row = StackLayout(size_hint_y=None, spacing=dp(6), padding=(0, dp(2)))
            row.bind(minimum_height=row.setter("height"))
            row.add_widget(Label(text=f"{i}.", size_hint=(None, None), size=(dp(26), dp(42)), color=INK, bold=True))
            for n in c["numbers"]:
                row.add_widget(Ball(text=f"{n:02d}", bg=list(color)))
            if c["bonus"] is not None:
                row.add_widget(Label(text="+", size_hint=(None, None), size=(dp(16), dp(42)), color=INK, bold=True))
                row.add_widget(Ball(text=f"{c['bonus']:02d}", bg=[0.95, 0.71, 0.14, 1]))
            box.add_widget(row)
        if draws:
            self._show_stats(data["draws"])
        else:
            self.ids.stats.text = self._footer()
        if not draws:
            self.ids.status.text = "Χωρίς κληρώσεις στη μνήμη: οι αριθμοί βγήκαν εντελώς τυχαία."

    # ------------------------------------------------------------ ενημέρωση
    def update_history(self):
        if self.busy:
            return
        self.busy = True
        game = self.game
        self.ids.upd.disabled = True
        self.ids.status.text = f"Λήψη κληρώσεων {L.GAMES[game]['name']} από τον ΟΠΑΠ…"
        wanted = 500

        def log(msg):
            Clock.schedule_once(lambda dt: setattr(self.ids.status, "text", msg))

        def work():
            try:
                draws = L.fetch_history(game, wanted, log)
                data = L.save(game, draws)
                err = ""
            except Exception as e:  # noqa: BLE001
                data = L.load(game)
                err = f"\n[color=#B4461B]Η ενημέρωση απέτυχε: {str(e)[:160]}. Κρατήθηκαν οι αποθηκευμένες κληρώσεις.[/color]"
            Clock.schedule_once(lambda dt: self._done(game, data, err))

        threading.Thread(target=work, daemon=True).start()

    def _done(self, game, data, err):
        self.busy = False
        self.ids.upd.disabled = False
        if game == self.game:
            self._show_info(data, err)


if __name__ == "__main__":
    TzokerApp().run()
