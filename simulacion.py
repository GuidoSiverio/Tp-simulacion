import numpy as np
import random
import pandas as pd
import matplotlib
matplotlib.use('Agg')  # Utiliza un backend no interactivo
import matplotlib.pyplot as plt

class Pedido:
    def __init__(self, id_pedido):
        self.id = id_pedido
        self.estado = "pendiente"  # Puede ser "pendiente", "producido" o "cancelado"

class Maquina:
    def __init__(self, id_maquina, limite_produccion):
        self.id = id_maquina
        self.limite_produccion = limite_produccion
        self.fallos = 0
        self.operativa = True
        self.pedidos_asignados = []
    
    def verificar_fallo(self):
        """Cada día, una máquina tiene un 5% de probabilidad de fallar."""
        if random.random() < 0.05:
            self.operativa = False
            self.fallos += 1
            return True
        return False
    
    def asignar_pedido(self, pedido):
        if self.operativa and len(self.pedidos_asignados) < self.limite_produccion:
            self.pedidos_asignados.append(pedido)
            pedido.estado = "producido"
            return True
        return False
    
    def reset(self):
        """Al inicio de cada día, se resetea la máquina (se repara si falló)."""
        self.operativa = True
        self.pedidos_asignados = []

class Simulacion:
    def __init__(self, dias=365, num_maquinas=7, limite_produccion=257):
        self.dias = dias
        self.num_maquinas = num_maquinas
        self.limite_produccion = limite_produccion
        self.maquinas = [Maquina(i, limite_produccion) for i in range(num_maquinas)]
        self.pedidos_perdidos = 0
        self.pedidos_fallados = 0
        self.pedidos_realizados = 0
        self.beneficio_total = 0
        self.fallos_totales = 0
        self.pedidos_generados = 0
    
    def generar_visitas(self, dia):
        """Genera la cantidad de visitas diarias según la fdp correspondiente."""
        if dia in self.eventos_especiales():
            return np.random.binomial(7500000, 0.8)  # Hot Sale / Black Friday
        elif 334 <= dia < 365:
            return np.random.binomial(5000000, 0.8)  # Diciembre
        else:
            return np.random.binomial(4000000, 0.766)  # Día normal
    
    def eventos_especiales(self):
        """Devuelve los días en los que hay eventos especiales (cada 3 meses)."""
        eventos = []
        for mes in range(0, 9, 3):
            eventos.extend(range(mes * 30, mes * 30 + 3))
        return eventos
    
    def ejecutar_simulacion(self):
        """Ejecuta la simulación día a día."""
        for dia in range(self.dias):
            # Generar visitas y pedidos
            visitas = self.generar_visitas(dia)
            conversiones = np.random.uniform(0.001, 0.005) * visitas  # 0.1% - 0.5% de visitas a publicación
            pedidos = int(conversiones * 0.02)  # 2% de conversión a ventas
            self.pedidos_generados += pedidos
            
            # Reiniciar máquinas al inicio del día
            for maquina in self.maquinas:
                maquina.reset()
            
            # Asignar pedidos a máquinas disponibles
            pedidos_pendientes = [Pedido(i) for i in range(pedidos)]
            for pedido in pedidos_pendientes:
                asignado = False
                for maquina in self.maquinas:
                    if maquina.asignar_pedido(pedido):
                        asignado = True
                        break
                if not asignado:
                    self.pedidos_perdidos += 1

            for maquina in self.maquinas:
                if maquina.verificar_fallo(): 
                    self.pedidos_fallados = len(maquina.pedidos_asignados)
                    self.fallos_totales += 1

            for pedido in pedidos_pendientes:
                if pedido.estado == "producido":
                    self.pedidos_realizados += 1
            
            # Calcular beneficio
            self.beneficio_total += (self.pedidos_realizados - self.pedidos_perdidos - self.pedidos_fallados) * 20000
            self.pedidos_fallados = 0
            self.pedidos_realizados = 0
        self.mostrar_resultados()
    
    def mostrar_resultados(self):
        """Muestra métricas finales de la simulación."""
        print("\n--- Resultados de la Simulación ---")
        print(f"Pedidos generados: {self.pedidos_generados}")
        print(f"Pedidos perdidos: {self.pedidos_perdidos}")
        print(f"Pedidos fallados: {self.pedidos_fallados}")
        print(f"Beneficio total anual: ${self.beneficio_total}")
        print(f"Fallos en máquinas: {self.fallos_totales}")
        print(f"Tasa de fallos en producción: {self.fallos_totales / self.dias:.2f} fallos/día")
        
        # Guardar en CSV
        # datos = pd.DataFrame({
        #     "Pedidos Generados": [self.pedidos_generados],
        #     "Pedidos Perdidos": [self.pedidos_perdidos],
        #     "Beneficio Total": [self.beneficio_total],
        #     "Fallos Totales": [self.fallos_totales],
        #     "Tasa de Fallos": [self.fallos_totales / self.dias]
        # })
        # datos.to_csv("resultados_simulacion.csv", index=False)
        
        # Graficar distribución de visitas
        dias = np.arange(self.dias)
        visitas = [self.generar_visitas(d) for d in dias]
        plt.figure(figsize=(10, 5))
        plt.plot(dias, visitas, label="Visitas Diarias", color='b')
        plt.xlabel("Día")
        plt.ylabel("Cantidad de Visitas")
        plt.title("Simulación de Visitas a la Categoría")
        plt.legend()
        plt.grid()
        plt.savefig("visitas_diarias.png")

# Ejecutar simulación
sim = Simulacion(dias=365, num_maquinas=4, limite_produccion=257)
sim.ejecutar_simulacion()
