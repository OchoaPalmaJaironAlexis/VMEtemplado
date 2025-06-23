import streamlit as st
import pandas as pd
import graphviz  # Cambio clave: importamos el módulo completo

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

def generar_arbol_decision(vme_a, vme_b, ingresos_a1, ingresos_a2, prob_a1, prob_a2, 
                          ingresos_b1, ingresos_b2, prob_b1, prob_b2, costo_estudio):
    """Genera un gráfico del árbol de decisión"""
    try:
        dot = graphviz.Digraph(comment='Árbol de Decisión')  # Usamos graphviz.Digraph directamente
        dot.attr(rankdir='LR', size='10,8', dpi='300')  # Mejor visualización
        
        # Nodo raíz
        dot.node('D', 'Decisión', shape='diamond', fontsize='12')
        
        # Opción A
        dot.node('A', 'Opción (b)\n(Sin estudio)', shape='box')
        dot.edge('D', 'A', label=f'VME: ${vme_a:,.2f}', fontsize='10')
        
        # Escenarios A
        dot.node('A1', f'Escenario 1\nProb: {prob_a1:.0%}\nIngreso: ${ingresos_a1:,.0f}')
        dot.node('A2', f'Escenario 2\nProb: {prob_a2:.0%}\nIngreso: ${ingresos_a2:,.0f}')
        dot.edge('A', 'A1')
        dot.edge('A', 'A2')
        
        # Opción B
        dot.node('B', 'Opción (c)\n(Con estudio)', shape='box')
        dot.edge('D', 'B', label=f'Costo: ${costo_estudio:,.0f}\nVME: ${vme_b:,.0f}')
        
        # Escenarios B
        dot.node('B1', f'Escenario 1\nProb: {prob_b1:.0%}\nNeto: ${ingresos_b1:,.0f}')
        dot.node('B2', f'Escenario 2\nProb: {prob_b2:.0%}\nNeto: ${ingresos_b2:,.0f}')
        dot.edge('B', 'B1')
        dot.edge('B', 'B2')
        
        return dot
        
    except Exception as e:
        st.error(f"Error al generar el gráfico: {str(e)}")
        st.info("Verifica que las dependencias de Graphviz estén instaladas")
        return None

def main():
    st.set_page_config(page_title="Calculador VME", page_icon="📈", layout="wide")
    st.title("Calculador de Valor Monetario Esperado (VME)")
    
    with st.expander("Instrucciones"):
        st.write("""
        1. Configura los parámetros en el panel izquierdo.
        2. Las probabilidades deben sumar 1.0.
        3. Los resultados se calcularán automáticamente.
        """)
    
    # Configuración de valores por defecto
    config = {
        'unidades_a1': 100000,
        'unidades_a2': 75000,
        'unidades_b1': 75000,
        'unidades_b2': 70000,
        'precio_a1': 550.0,
        'precio_a2': 550.0,
        'precio_b1': 750.0,
        'precio_b2': 750.0,
        'prob_a1': 0.6,
        'prob_a2': 0.4,
        'prob_b1': 0.7,
        'prob_b2': 0.3,
        'costo_estudio': 100000.0
    }
    
    # Interfaz de usuario
    personalizar = st.sidebar.toggle("Personalizar valores", True)
    
    if personalizar:
        st.sidebar.header("Parámetros Opción (b)")
        col1, col2 = st.sidebar.columns(2)
        config['unidades_a1'] = col1.number_input("Unidades Esc. 1 (b)", min_value=0, value=config['unidades_a1'])
        config['precio_a1'] = col2.number_input("Precio unitario ($)", min_value=0.0, value=float(config['precio_a1']), format="%.2f")
        
        col3, col4 = st.sidebar.columns(2)
        config['unidades_a2'] = col3.number_input("Unidades Esc. 2 (b)", min_value=0, value=config['unidades_a2'])
        config['precio_a2'] = col4.number_input("Precio unitario ($)", min_value=0.0, value=float(config['precio_a2']), format="%.2f")
        
        prob_a = pedir_probabilidades("Opción b")
        if prob_a[0] is not None:
            config['prob_a1'], config['prob_a2'] = prob_a
        
        st.sidebar.header("Parámetros Opción (c)")
        col5, col6 = st.sidebar.columns(2)
        config['unidades_b1'] = col5.number_input("Unidades Esc. 1 (c)", min_value=0, value=config['unidades_b1'])
        config['precio_b1'] = col6.number_input("Precio unitario ($)", min_value=0.0, value=float(config['precio_b1']), format="%.2f")
        
        col7, col8 = st.sidebar.columns(2)
        config['unidades_b2'] = col7.number_input("Unidades Esc. 2 (c)", min_value=0, value=config['unidades_b2'])
        config['precio_b2'] = col8.number_input("Precio unitario ($)", min_value=0.0, value=float(config['precio_b2']), format="%.2f")
        
        config['costo_estudio'] = st.sidebar.number_input("Costo estudio ($)", min_value=0.0, value=float(config['costo_estudio']), format="%.2f")
        prob_b = pedir_probabilidades("Opción c")
        if prob_b[0] is not None:
            config['prob_b1'], config['prob_b2'] = prob_b
    
    # Validación final
    if None in [config['prob_a1'], config['prob_a2'], config['prob_b1'], config['prob_b2']]:
        st.warning("Ajusta las probabilidades para que sumen 1.0 en ambas opciones")
        st.stop()
    
    # Cálculos
    ingresos_a1, ingresos_a2, vme_a = calcular_vme_opcion_a(
        config['unidades_a1'], config['precio_a1'], config['prob_a1'],
        config['unidades_a2'], config['precio_a2'], config['prob_a2']
    )
    
    ingresos_b1, ingresos_b2, vme_b = calcular_vme_opcion_b(
        config['unidades_b1'], config['precio_b1'], config['prob_b1'],
        config['unidades_b2'], config['precio_b2'], config['prob_b2'],
        config['costo_estudio']
    )
    
    # Resultados
    mostrar_resultados("Opción (b)", ingresos_a1, config['prob_a1'], ingresos_a2, config['prob_a2'], vme_a)
    mostrar_resultados("Opción (c)", ingresos_b1, config['prob_b1'], ingresos_b2, config['prob_b2'], vme_b, config['costo_estudio'])
    
    st.divider()
    st.header("Recomendación")
    mejor_opcion = "(c)" if vme_b > vme_a else "(b)"
    st.success(f"**Elegir la OPCIÓN {mejor_opcion}** - VME: ${max(vme_a, vme_b):,.2f}")
    
    # Gráfico comparativo
    st.bar_chart(pd.DataFrame({
        "Opción": ["(b)", "(c)"],
        "VME": [vme_a, vme_b]
    }).set_index("Opción"))
    
    # Árbol de decisión
    st.divider()
    st.header("Árbol de Decisión")
    arbol = generar_arbol_decision(
        vme_a, vme_b,
        ingresos_a1, ingresos_a2, config['prob_a1'], config['prob_a2'],
        ingresos_b1, ingresos_b2, config['prob_b1'], config['prob_b2'],
        config['costo_estudio']
    )
    
    if arbol:
        st.graphviz_chart(arbol)
    else:
        st.warning("""
        El gráfico del árbol no se pudo generar. Verifica que:
        1. El archivo `packages.txt` existe y contiene `graphviz`
        2. El archivo `requirements.txt` incluye `python-graphviz`
        """)

if __name__ == "__main__":
    main()
