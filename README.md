# FarmaHub | Gestão CAF

Aplicação Streamlit para análise automatizada de pedidos, cálculo de recomendação de envio e separação FEFO por lote.

## Arquivos

- `app.py` — aplicação principal.
- `requirements.txt` — dependências.
- `secrets.toml.example` — modelo das credenciais.
- `.gitignore` — impede o envio de `secrets.toml` ao GitHub.

## Executar localmente

```bash
pip install -r requirements.txt
streamlit run app.py
```

Crie `.streamlit/secrets.toml` com:

```toml
usuario = "farmacia"
senha = "SUA_SENHA"
```

## Publicar no Streamlit Cloud

1. Suba `app.py`, `requirements.txt`, `README.md`, `.gitignore` e `secrets.toml.example` para o GitHub.
2. Não envie `.streamlit/secrets.toml`.
3. No Streamlit Cloud, selecione o repositório e o arquivo `app.py`.
4. Em **Settings → Secrets**, cadastre `usuario` e `senha`.
5. Publique/reinicie a aplicação.

## Formato das planilhas

A planilha de pedido precisa conter, após a padronização dos nomes das colunas:

- `unidade`
- `tipo_produto`
- `produto`
- `cm`
- `estoque`

- ## 📄 Licença e Direitos Autorais

Este projeto está sob uma **Licença Proprietária**. Todos os direitos estão reservados a **Cristiano Amorim**. O acesso ao código e ao link da aplicação é restrito e não pode ser copiado ou reutilizado sem autorização expressa. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.
- opcionalmente `codigo_produto`
- opcionalmente `demanda_nao_atendida`

A planilha de estoque CAF precisa conter `tipo_produto`, `produto` e uma das colunas `quantidade` ou `quantidade_estoque_lote`. Para a separação FEFO, a coluna `validade` é necessária.
