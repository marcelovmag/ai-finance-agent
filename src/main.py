import os
import json
from google import genai
from google.genai import types
from pydantic import BaseModel, Field

from dotenv import load_dotenv
load_dotenv()

from batcher import Batcher, TransacaoExtrato

# 1. Inicializa o cliente. Ele busca automaticamente a variável de ambiente GEMINI_API_KEY.
client = genai.Client()

# 2. Definimos a estrutura (Schema) exata que queremos que a IA retorne
class CategoriaTransacao(BaseModel):
    data: str = Field(description="A data da transação no formato DD/MM/AAAA.")
    valor: float = Field(description="O valor da transação em reais (R$).")
    categoria: str = Field(description="A categoria financeira da transação. Ex: Alimentação, Transporte, Moradia, Lazer, Saúde, Educação, Outros.")
    estabelecimento: str = Field(description="O nome limpo e compreensível do estabelecimento (removendo códigos e asteriscos).")
    justificativa: str = Field(description="Uma frase curta justificando a escolha da categoria.")

class LoteTransacoes(BaseModel):
    transacoes: list[CategoriaTransacao] = Field(
        min_length=1,
        description="Lista de transações já classificadas."
    )

def classificar_extrato(lote_formatado : str) -> str:
    """
    Envia um lote de transações formatadas para o Gemini e retorna a classificação em formato JSON seguro.
    """
    prompt = f"""
    Você é um assistente de inteligência financeira.
    Analise as seguintes transações bancárias extraídas de um extrato e classifique-as.
    Considere as seguintes categorias: Alimentação, Transporte, Moradia, Lazer, Saúde, Educação, Outros.
    Para cada transação, forneça:
    - data: A data da transação no formato DD/MM/AAAA.
    - valor: O valor da transação em reais (R$).
    - categoria: A categoria financeira da transação.
    - estabelecimento: O nome limpo e compreensível do estabelecimento (removendo códigos e asteriscos).
    - justificativa: Uma frase curta justificando a escolha da categoria.
    Retorne a resposta no formato JSON seguro, seguindo o schema definido para LoteTransacoes
    Aqui está o lote de transações a ser classificado:
    
    {lote_formatado}"""

    # 3. Faz a chamada ao modelo definindo o schema de resposta
    response = client.models.generate_content(
        model='gemini-3.6-flash', # Modelo atual recomendado para novos usuários
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=LoteTransacoes,
            automatic_function_calling=types.AutomaticFunctionCallingConfig(
                disable=True
            ),
            temperature=0.1, # Temperatura próxima de zero para respostas mais precisas e analíticas
        ),
    )
    
    return response.text

# --- Testando o Agente ---
if __name__ == "__main__":

    batcher = Batcher("extratos", tamanho_maximo_lote=25)

    len_lotes = len(batcher.get_lotes())

    print(f"Total de transações carregadas: {len(batcher.get_transacoes())}")
    print(f"Total de lotes: {len_lotes}")
    
    os.makedirs("saida", exist_ok=True)
    resultados = []

    for indice_lote, lote in enumerate(batcher.get_lotes(), start=1):

        if indice_lote % 3 == 0:
            print("Intervalo atingido. Salvando resultados parciais e aguardando 60 segundos...")
            with open("saida/consolidado.json", "w", encoding="utf-8") as arquivo:
                json.dump(resultados, arquivo, ensure_ascii=False, indent=2)
            print("Resultados parciais salvos.")
            print("Aguardando 60 segundos para evitar sobrecarga na API...")
            time.sleep(60)

        print(f"Processando lote {indice_lote}/{len_lotes} com {len(lote)} transações...")

        output_json = classificar_extrato(batcher.formatar_lote_para_prompt(lote))
        print(f"Processamento do lote {indice_lote} concluído. Output: {output_json[:50]}...")  # Mostra apenas os primeiros 100 caracteres do resultado
        output_dict = json.loads(output_json)

        resultados.append({
            "lote": indice_lote,
            "transacoes": output_dict["transacoes"]
        })

    with open("saida/consolidado.json", "w", encoding="utf-8") as arquivo:
        json.dump(resultados, arquivo, ensure_ascii=False, indent=2)
        
        
