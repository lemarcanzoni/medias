import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import plotly.express as px


# Função para carregar o CSV
def carregar_dados():
    uploaded_file = st.file_uploader("Escolha um arquivo CSV", type=["csv"])
    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
        # Limpeza dos dados
        df.columns = df.columns.str.strip()  # Remover espaços extras nos nomes das colunas
        df['Data/Hora'] = pd.to_datetime(df['Data/Hora'], errors='coerce')  # Garantir que Data/Hora seja datetime
        return df
    else:
        return None


# Função para filtrar dados
def filtrar_dados(df, periodo='Dia'):
    if periodo == 'Semana':
        df['Semana'] = df['Data/Hora'].dt.isocalendar().week
        return df.groupby('Semana').agg({'Consumo_kWh': 'sum', 'Custo_Total': 'sum'})
    elif periodo == 'Dia':
        df['Dia'] = df['Data/Hora'].dt.date
        return df.groupby('Dia').agg({'Consumo_kWh': 'sum', 'Custo_Total': 'sum'})
    return df


# Função para gerar gráficos
def gerar_graficos(df):
    # 1. Gráfico de barras: Consumo total por dia com destaque para o dia com maior consumo
    fig1, ax1 = plt.subplots(figsize=(10, 6))
    df['Consumo_kWh'].plot(kind='bar', color='skyblue', ax=ax1)

    # Destaque para o dia com maior consumo
    max_consumo = df['Consumo_kWh'].max()
    max_consumo_dia = df['Consumo_kWh'].idxmax()
    ax1.bar(max_consumo_dia, max_consumo, color='red', label=f'Dia com maior consumo: {max_consumo_dia}')
    ax1.set_title('Consumo Total por Dia')
    ax1.set_xlabel('Dia')
    ax1.set_ylabel('Consumo (kWh)')
    ax1.legend()

    st.pyplot(fig1)

    # 2. Gráfico de linha: Consumo horário médio
    df['Hora'] = df['Data/Hora'].dt.hour
    consumo_horario = df.groupby('Hora').agg({'Consumo_kWh': 'mean'})

    fig2 = px.line(consumo_horario, x=consumo_horario.index, y='Consumo_kWh',
                   labels={'Hora': 'Hora do Dia', 'Consumo_kWh': 'Consumo Médio (kWh)'},
                   title='Consumo Médio por Hora')
    st.plotly_chart(fig2)

    # 3. Gráfico de pizza: Distribuição do consumo por categorias (Pico/Noturno)
    df['Categoria'] = df['Hora'].apply(lambda x: 'Pico' if 8 <= x <= 18 else 'Noturno')
    consumo_categoria = df.groupby('Categoria').agg({'Consumo_kWh': 'sum'}).reset_index()

    fig3 = px.pie(consumo_categoria, names='Categoria', values='Consumo_kWh',
                  title='Distribuição do Consumo por Categoria')
    st.plotly_chart(fig3)


# Função para mostrar o consumo total e custo total
def exibir_resumo(df):
    consumo_total = df['Consumo_kWh'].sum()
    custo_total = df['Custo_Total'].sum()
    st.write(f"**Consumo Total (kWh):** {consumo_total:.2f} kWh")
    st.write(f"**Custo Total (R$):** R${custo_total:.2f}")


# Função principal do app
def main():
    st.title("Analisador de Consumo de Energia Residencial")

    # Carregar dados
    df = carregar_dados()
    if df is not None:
        # Seleção do período de filtro
        periodo = st.selectbox('Escolha o período de análise:', ['Dia', 'Semana'])

        # Filtrar dados
        dados_filtrados = filtrar_dados(df, periodo)

        # Exibir os dados filtrados
        st.write(dados_filtrados)

        # Exibir resumo do consumo total
        exibir_resumo(dados_filtrados)

        # Gerar gráficos
        gerar_graficos(dados_filtrados)
    else:
        st.write("Por favor, faça o upload de um arquivo CSV.")


if __name__ == "__main__":
    main()
