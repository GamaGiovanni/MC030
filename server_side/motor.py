# motor.py

import fnmatch

class MicrohistoriaEngine:
    def __init__(self, historia: dict):
        self.historia = historia
        self.estagio_atual = historia["estagio_inicial"]

    def estagio(self) -> dict:
        return self.historia["estagios"][self.estagio_atual]

    def is_terminal(self) -> bool:
        return self.estagio().get("terminal", False)

    def processar_evento(self, evento: str) -> dict:
        if self.is_terminal():
            return self.estagio()  # história encerrada, ignora novos eventos

        transicoes = self.estagio().get("transicoes", {})
        proximo = self._resolver_transicao(evento, transicoes)

        if proximo and proximo in self.historia["estagios"]:
            self.estagio_atual = proximo

        return self.estagio()

    def _resolver_transicao(self, evento: str, transicoes: dict):
        if evento in transicoes:
            return transicoes[evento]
        for padrao, destino in transicoes.items():
            if fnmatch.fnmatch(evento, padrao):
                return destino
        return transicoes.get("*")

    def reiniciar(self):
        self.estagio_atual = self.historia["estagio_inicial"]

    def trocar_historia(self, nova_historia: dict):
        self.historia = nova_historia
        self.estagio_atual = nova_historia["estagio_inicial"]

    def serializar(self) -> dict:
        return {
            "historia_id":     self.historia["id"],
            "historia_titulo": self.historia["titulo"],
            "estagio_atual":   self.estagio_atual,
            "narrativa":       self.estagio().get("narrativa", ""),
            "terminal":        self.is_terminal(),
        }