import streamlit as st
import pandas as pd
from graphviz import Digraph

def pedir_probabilidades(nombre):
    st.sidebar.markdown(f"### Probabilidades para {nombre}")
    col1, col2 = st.sidebar.columns(2)
    prob1 = col1.number_input(f"Prob. Escenario 1 ({nombre})", 0.0, 1.0, 0.5, 0.01, key=f"{nombre}_prob1")
    prob2 = col2.number_input(f"Prob. Escenario 2 ({nombre})", 0.0, 1.0, 0.5, 0.01, key=f"{nombre}_prob2")
    
    if abs((prob1 + prob2) - 1.0) > 1e-6:
        st.sidebar.error("Las probabilidades deben sumar 1.0")
        return None, None
    return prob1, prob2

def calcular_vme_opcion_a(unidades_a1, precio_a1, prob_a1, unidades_a2, precio_a2, prob_a2):
    ingresos_a1 = unidades_a1 * precio_a1
    ingresos_a2 = unidades_a2 * precio_a2
    vme_a = (ingresos_a1 * prob_a1) + (ingresos_a2 * prob_a2)
    return ingresos_a1, ingresos_a2, vme_a

def calcular_vme_opcion_b(unidades_b1, precio_b1, prob_b1, unidades_b2, precio_b2, prob_b2, costo_estudio):
    ingresos_brutos_b1 = unidades_b1 * precio_b1
    ingresos_netos_b1 = ingresos_brutos_b1 - costo_estudio
    ingresos_brutos_b2 = unidades_b2 * precio_b2
    ingresos_netos_b2 = ingresos_brutos_b2 - costo_estudio
    vme_b = (ingresos_netos_b1 * prob_b1) + (ingresos_netos_b2 * prob_b2)
    return ingresos_netos_b1, ingresos_netos_b2, vme_b

def mostrar_resultados(nombre_opcion, ingreso1, prob1, ingreso2, prob2, vme, costo_estudio=None):
    st.subheader(f"{nombre_opcion}")
    
    data = {
        "Escenario": [1, 2],
        "Probabilidad": [prob1, prob2],
        "Ingresos": [ingreso1, ingreso2]
    }
    
    if costo_estudio is not None:
        data["Costo Estudio"] = [costo_estudio, costo_estudio]
        data["Ingresos Netos"] = [ingreso1, ingreso2]
    
    df = pd.DataFrame(data)
    st.dataframe(df.style.format("{:,.2f}"), hide_index=True)
    
    st.metric(f"VME {nombre_opcion}", f"${vme:,.2f}")

def generar_arbol_decision(vme_a, vme_b, ingresos_a1, ingresos_a2, prob_a1, prob_a2, ingresos_b1, ingresos_b2, prob_b1, prob_b2, costo_estudio):
    """Genera un gráfico del árbol de decisión usando graphviz."""
    dot = Digraph(comment='Árbol de Decisión')
    dot.attr(rankdir='LR')  # Orientación horizontal

    # Nodo raíz (decisión)
    dot.node('D', 'Decisión', shape='diamond')

    # Opción A (b)
    dot.node('A', 'Opción (b)\n(Sin estudio)', shape='box')
    dot.edge('D', 'A', label=f'VME: ${vme_a:,.2f}')

    # Escenarios de la Opción A
    dot.node('A1', f'Escenario 1\nProb: {prob_a1:.2f}\nIngreso: ${ingresos_a1:,.2f}', shape='ellipse')
    dot.node('A2', f'Escenario 2\nProb: {prob_a2:.2f}\nIngreso: ${ingresos_a2:,.2f}', shape='ellipse')
    dot.edge('A', 'A1')
    dot.edge('A', 'A2')

    # Opción B (c)
    dot.node('B', 'Opción (c)\n(Con estudio)', shape='box')
    dot.edge('D', 'B', label=f'Costo: ${costo_estudio:,.2f}\nVME: ${vme_b:,.2f}')

    # Escenarios de la Opción B
    dot.node('B1', f'Escenario 1\nProb: {prob_b1:.2f}\nIngreso Neto: ${ingresos_b1:,.2f}', shape='ellipse')
    dot.node('B2', f'Escenario 2\nProb: {prob_b2:.2f}\nIngreso Neto: ${ingresos_b2:,.2f}', shape='ellipse')
    dot.edge('B', 'B1')
    dot.edge('B', 'B2')

    return dot

def main():
    st.set_page_config(page_title="Calculador VME", page_icon="📈", layout="wide")
    st.title("Calculador de Valor Monetario Esperado (VME)")
    
    with st.expander("Instrucciones"):
        st.write("""
        1. Configura los parámetros en el panel izquierdo.
        2. Las probabilidades deben sumar 1.0.
        3. Los resultados se calcularán automáticamente.
        """)
    
    # Valores por defecto
    unidades_a1, unidades_a2 = 100000, 75000
    unidades_b1, unidades_b2 = 75000, 70000
    precio_a1 = precio_a2 = 550.0
    precio_b1 = precio_b2 = 750.0
    prob_a1, prob_a2 = 0.6, 0.4
    prob_b1, prob_b2 = 0.7, 0.3
    costo_estudio = 100000.0
    
    personalizar = st.sidebar.toggle("Personalizar valores", True, key="personalizar_toggle")
    
    if personalizar:
        st.sidebar.header("Parámetros Opción (b)")
        col1, col2 = st.sidebar.columns(2)
        unidades_a1 = col1.number_input("Unidades Esc. 1 (b)", min_value=0, max_value=1000000, value=unidades_a1, key="unidades_a1")
        precio_a1 = col2.number_input("Precio unitario ($)", min_value=0.0, max_value=10000.0, value=float(precio_a1), step=1.0, format="%.2f", key="precio_a1")
        
        col3, col4 = st.sidebar.columns(2)
        unidades_a2 = col3.number_input("Unidades Esc. 2 (b)", min_value=0, max_value=1000000, value=unidades_a2, key="unidades_a2")
        precio_a2 = col4.number_input("Precio unitario ($)", min_value=0.0, max_value=10000.0, value=float(precio_a2), step=1.0, format="%.2f", key="precio_a2")
        
        prob_result = pedir_probabilidades("Opción b")
        if prob_result[0] is not None:
            prob_a1, prob_a2 = prob_result
        
        st.sidebar.header("Parámetros Opción (c)")
        col5, col6 = st.sidebar.columns(2)
        unidades_b1 = col5.number_input("Unidades Esc. 1 (c)", min_value=0, max_value=1000000, value=unidades_b1, key="unidades_b1")
        precio_b1 = col6.number_input("Precio unitario ($)", min_value=0.0, max_value=10000.0, value=float(precio_b1), step=1.0, format="%.2f", key="precio_b1")
        
        col7, col8 = st.sidebar.columns(2)
        unidades_b2 = col7.number_input("Unidades Esc. 2 (c)", min_value=0, max_value=1000000, value=unidades_b2, key="unidades_b2")
        precio_b2 = col8.number_input("Precio unitario ($)", min_value=0.0, max_value=10000.0, value=float(precio_b2), step=1.0, format="%.2f", key="precio_b2")
        
        costo_estudio = st.sidebar.number_input("Costo estudio ($)", min_value=0.0, max_value=1000000.0, value=float(costo_estudio), step=1000.0, format="%.2f", key="costo_estudio")
        prob_result = pedir_probabilidades("Opción c")
        if prob_result[0] is not None:
            prob_b1, prob_b2 = prob_result
    
    # Validación final
    if None in [prob_a1, prob_a2, prob_b1, prob_b2]:
        st.warning("Por favor ajusta las probabilidades para que sumen 1.0 en ambas opciones")
        st.stop()
    
    # Cálculos
    ingresos_a1, ingresos_a2, vme_a = calcular_vme_opcion_a(
        unidades_a1, precio_a1, prob_a1, unidades_a2, precio_a2, prob_a2
    )
    
    ingresos_b1, ingresos_b2, vme_b = calcular_vme_opcion_b(
        unidades_b1, precio_b1, prob_b1, unidades_b2, precio_b2, prob_b2, costo_estudio
    )
    
    # Resultados
    mostrar_resultados("Opción (b)", ingresos_a1, prob_a1, ingresos_a2, prob_a2, vme_a)
    mostrar_resultados("Opción (c)", ingresos_b1, prob_b1, ingresos_b2, prob_b2, vme_b, costo_estudio)
    
    st.divider()
    st.header("Recomendación")
    
    if vme_b > vme_a:
        st.success(f"**Elegir la OPCIÓN (c)** - VME: ${vme_b:,.2f} vs ${vme_a:,.2f}")
    else:
        st.success(f"**Elegir la OPCIÓN (b)** - VME: ${vme_a:,.2f} vs ${vme_b:,.2f}")
    
    # Gráfico comparativo
    chart_data = pd.DataFrame({
        "Opción": ["(b)", "(c)"],
        "VME": [vme_a, vme_b]
    })
    st.bar_chart(chart_data.set_index("Opción"), use_container_width=True)

    # Árbol de decisión
    st.divider()
    st.header("Árbol de Decisión")
    arbol = generar_arbol_decision(
        vme_a, vme_b,
        ingresos_a1, ingresos_a2, prob_a1, prob_a2,
        ingresos_b1, ingresos_b2, prob_b1, prob_b2,
        costo_estudio
    )
    st.graphviz_chart(arbol)

if __name__ == "__main__":
    main()