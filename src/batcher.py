from __future__ import annotations

import csv
import re
from dataclasses import dataclass
from pathlib import Path


@dataclass(slots=True)
class TransacaoExtrato:
    data: str
    valor: float
    descricao_prompt: str
    arquivo_origem: str


class Batcher:
    def __init__(self, pasta_extratos: str | Path, tamanho_maximo_lote: int = 25):
        self.pasta_extratos = Path(pasta_extratos)
        self.tamanho_maximo_lote = tamanho_maximo_lote
        self.transacoes: list[TransacaoExtrato] = self._carregar_transacoes_da_pasta()
        self.lotes: list[list[TransacaoExtrato]] = self._dividir_em_lotes(
            self.transacoes,
            tamanho_maximo=self.tamanho_maximo_lote,
        )

    def get_lotes(self) -> list[list[TransacaoExtrato]]:
        return self.lotes

    def get_transacoes(self) -> list[TransacaoExtrato]:
        return self.transacoes

    @staticmethod
    def _normalizar_texto(texto: str) -> str:
        return re.sub(r"\s+", " ", texto or "").strip()

    @staticmethod
    def _fragmento_ruidoso(fragmento: str) -> bool:
        texto = fragmento.strip()
        if not texto:
            return True

        if "•" in texto:
            return True

        texto_upper = texto.upper()
        marcadores_ruidosos = (
            "AGÊNCIA:",
            "AGENCIA:",
            "CONTA:",
            "BCO ",
            "BANCO ",
            "ITAÚ",
            "ITAU",
            "CAIXA ECONOMICA",
            "BRADESCO",
            "SANTANDER",
            "SICOOB",
            "PICPAY",
            "MERCADO PAGO",
            "CNPJ",
            "CPF",
        )
        return any(marcador in texto_upper for marcador in marcadores_ruidosos)

    @classmethod
    def _limpar_descricao_para_prompt(cls, descricao: str) -> str:
        texto = cls._normalizar_texto(descricao)
        if not texto:
            return ""

        partes = [parte.strip(" -") for parte in re.split(r"\s+-\s+", texto) if parte.strip(" -")]
        if not partes:
            return texto

        mantidas: list[str] = []
        for parte in partes:
            if cls._fragmento_ruidoso(parte):
                break
            mantidas.append(parte)
            if len(mantidas) == 2:
                break

        return " - ".join(mantidas) if mantidas else texto

    @staticmethod
    def _parse_valor(texto: str) -> float:
        return float(texto.strip().replace(",", "."))

    def _carregar_transacoes_csv(self, caminho_arquivo: Path) -> list[TransacaoExtrato]:
        caminho = Path(caminho_arquivo)
        transacoes: list[TransacaoExtrato] = []

        with caminho.open("r", encoding="utf-8-sig", newline="") as arquivo:
            leitor = csv.DictReader(arquivo)
            for linha in leitor:
                valor_original = self._parse_valor(linha["Valor"])

                # Ignorando transações de crédito (valores positivos) para focar apenas em gastos
                if valor_original >= 0:
                    continue

                descricao_original = self._normalizar_texto(linha["Descrição"])
                descricao_prompt = self._limpar_descricao_para_prompt(descricao_original)

                transacoes.append(
                    TransacaoExtrato(
                        data=self._normalizar_texto(linha["Data"]),
                        valor=abs(valor_original),
                        descricao_prompt=descricao_prompt,
                        arquivo_origem=caminho.name,
                    )
                )

        return transacoes

    def _carregar_transacoes_da_pasta(self) -> list[TransacaoExtrato]:
        pasta = self.pasta_extratos
        transacoes: list[TransacaoExtrato] = []

        for arquivo_csv in sorted(pasta.rglob("*.csv")):
            transacoes.extend(self._carregar_transacoes_csv(arquivo_csv))

        return transacoes

    @staticmethod
    def _dividir_em_lotes(
        transacoes: list[TransacaoExtrato],
        tamanho_maximo: int,
    ) -> list[list[TransacaoExtrato]]:
        if not transacoes:
            return []

        if tamanho_maximo <= 0:
            raise ValueError("tamanho_maximo deve ser maior que zero")

        return [transacoes[indice:indice + tamanho_maximo] for indice in range(0, len(transacoes), tamanho_maximo)]

    @staticmethod
    def _transacao_para_prompt(transacao: TransacaoExtrato) -> dict[str, object]:
        return {
            "data": transacao.data,
            "valor": transacao.valor,
            "direcao": transacao.direcao,
            "descricao": transacao.descricao_prompt,
        }

    def lote_para_prompt(self, lote: list[TransacaoExtrato]) -> list[dict[str, object]]:
        return [self._transacao_para_prompt(transacao) for transacao in lote]

    def formatar_lote_para_prompt(self, lote: list[TransacaoExtrato]) -> str:
        linhas = []
        for transacao in lote:
            linhas.append(
                f"{transacao.data} | R$ {transacao.valor:.2f} | {transacao.descricao_prompt}"
            )
        return "\n".join(linhas)


if __name__ == "__main__":
    batcher = Batcher("extratos", tamanho_maximo_lote=25)
    print(f"Total de transações carregadas: {len(batcher.get_transacoes())}")
    print(f"Total de lotes: {len(batcher.get_lotes())}")
    print("Exemplo de lote formatado para prompt:")
    if batcher.get_lotes():
        print(batcher.formatar_lote_para_prompt(batcher.get_lotes()[0]))