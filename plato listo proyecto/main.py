
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.properties import ObjectProperty

import os
import json
import datetime
import logging
import time

class MenuScreen(Screen):
    pass

class MeseroScreen(Screen):
    def enviar_pedido(self):
        mesa = self.ids.mesa_input.text
        pedido = self.ids.pedido_input.text
        if mesa and pedido:
            chef_screen = self.manager.get_screen('chef')
            chef_screen.agregar_pedido(mesa, pedido)
            self.ids.mesa_input.text = ''
            self.ids.pedido_input.text = ''
            # Registrar métrica de envío de pedido
            try:
                App.get_running_app().record_event('Métrica 1: Enviar Pedido', {'mesa': mesa, 'pedido': pedido})
            except Exception:
                pass

class ChefScreen(Screen):
    def agregar_pedido(self, mesa, pedido):
        pedidos_layout = self.ids.pedidos_layout
        from kivy.uix.label import Label
        pedidos_layout.add_widget(Label(text=f"Mesa {mesa}: {pedido}", font_size=18))

class PlatoListoApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Configurar logger de métricas: escribe JSON en metrics.log
        try:
            metrics_path = os.path.join(os.path.dirname(__file__), 'metrics.log')
            self.metrics_logger = logging.getLogger('plato_listo_metrics')
            self.metrics_logger.setLevel(logging.INFO)
            # Evitar añadir múltiples handlers si el logger ya fue configurado
            if not any(isinstance(h, logging.FileHandler) and getattr(h, 'baseFilename', None) == os.path.abspath(metrics_path) for h in self.metrics_logger.handlers):
                fh = logging.FileHandler(metrics_path, encoding='utf-8')
                fh.setLevel(logging.INFO)
                # El mensaje será el JSON ya formateado por record_event
                fh.setFormatter(logging.Formatter('%(message)s'))
                self.metrics_logger.addHandler(fh)
        except Exception as e:
            print('No se pudo configurar logger de métricas:', e)

    def build(self):
        Builder.load_file("main.kv")
        sm = ScreenManager()
        sm.add_widget(MenuScreen(name='menu'))
        sm.add_widget(MeseroScreen(name='mesero'))
        sm.add_widget(ChefScreen(name='chef'))
        return sm

    def record_event(self, name, details=None):
        """Registra una métrica simple escribiendo una línea JSON en `metrics.log`.

        name: nombre del evento (string)
        details: diccionario con detalles opcionales
        """
        entry = {
            'timestamp': datetime.datetime.utcnow().isoformat() + 'Z',
            'event': name,
        }
        if details is not None:
            entry['details'] = details

        try:
            # Usar logging estándar para escribir la línea JSON en el archivo
            msg = json.dumps(entry, ensure_ascii=False)
            if hasattr(self, 'metrics_logger'):
                self.metrics_logger.info(msg)
            else:
                # Fallback: escribir directamente si no hay logger
                path = os.path.join(os.path.dirname(__file__), 'metrics.log')
                with open(path, 'a', encoding='utf-8') as f:
                    f.write(msg + '\n')
        except Exception as e:
            # No interrumpir la app si falla el registro; imprimir para diagnóstico
            print('Error al registrar métrica:', e)

    def on_start(self):
        """Se ejecuta cuando la app arranca; guardamos timestamp de inicio y registramos evento."""
        try:
            # Guardamos inicio en dos formas: datetime para ISO y time.time() para cálculo directo si se desea
            self._start_time = datetime.datetime.utcnow()
            self._start_time_ts = time.time()
            self.record_event('Métrica 1: Inicio App', {'ts': self._start_time.isoformat() + 'Z'})
        except Exception as e:
            print('Error en on_start:', e)

    def on_stop(self):
        """Se ejecuta al cerrar la app; calcula duración y registra la métrica."""
        try:
            end_time = datetime.datetime.utcnow()
            start_time = getattr(self, '_start_time', None)
            # Preferir el cálculo preciso usando time.time() si está disponible
            duration_seconds = None
            if hasattr(self, '_start_time_ts'):
                duration_seconds = time.time() - self._start_time_ts
            elif start_time is not None:
                duration_seconds = (end_time - start_time).total_seconds()

            details = {
                'start_ts': start_time.isoformat() + 'Z' if start_time is not None else None,
                'end_ts': end_time.isoformat() + 'Z',
                'duration_seconds': duration_seconds,
            }
            self.record_event('Métrica 1: Duración Sesión', details)
        except Exception as e:
            print('Error en on_stop al registrar duración:', e)

if __name__ == '__main__':
    PlatoListoApp().run()
