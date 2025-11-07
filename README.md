
## OCR de visografemas ELiS com CNN e segmentação por componentes

> Apresentação em slides e em vídeo estão no final desde README.

Reconhecimento Óptico de Visografemas (OCR) do sistema ELiS a partir de imagens sintéticas renderizadas de uma fonte dedicada. O projeto gera um dataset de visografemas, treina uma CNN para classificação por símbolo (em Unicode no formato U+XXXX) e avalia duas abordagens de segmentação para OCR em imagens com múltiplos visografemas.

- Fonte de dados: fonte ELiS (arquivo TTF) renderizada para 64×64 px, fundo branco e glifo preto.
- Modelo: CNN simples com 3 blocos Conv2D+MaxPool, Flatten, Dense(256), Dropout(0.5), saída softmax.
- Entradas do modelo: imagens em escala de cinza 64×64, com normalização interna via `Rescaling(1./255)`.
- Saída: índice de classe mapeado para rótulos U+XXXX (salvos em `class_names.json`).
- Notebooks principais:
  - Análise de fonte: [notebooks/font_analysis.ipynb](notebooks/font_analysis.ipynb)
  - Geração do dataset: [notebooks/gererate_dataset.ipynb](notebooks/gererate_dataset.ipynb)
  - Treinamento: [notebooks/train_model.ipynb](notebooks/train_model.ipynb)
  - Predição unitária: [notebooks/prediction.ipynb](notebooks/prediction.ipynb)
  - Geração de imagem de teste (palavra “rosa”): [notebooks/generate_ocr_image_test.ipynb](notebooks/generate_ocr_image_test.ipynb)
  - OCR por contornos: [notebooks/ocr_contourns.ipynb](notebooks/ocr_contourns.ipynb)
  - OCR por agrupamento de componentes: [notebooks/ocr_groupment.ipynb](notebooks/ocr_groupment.ipynb)

Arquivo de modelo treinado: [data/processed/modelo_ocr_simbolos.keras](data/processed/modelo_ocr_simbolos.keras)  
Imagem de teste: [data/raw/ocr_test_image.png](data/raw/ocr_test_image.png)


### Objetivos

- Construir um dataset sintético balanceado de visografemas ELiS a partir de uma fonte TTF, com augmentations.
- Treinar um classificador de visografemas com alto desempenho em 64×64 px.
- Avaliar técnicas de segmentação para OCR em sequências de visografemas:
  - Segmentação por contornos individuais.
  - Segmentação por agrupamento de componentes próximos (símbolos compostos).

### Resultados e alcance

- Classificação de visografemas isolados: acurácia de teste em torno de $95\\%$.
- OCR de palavras:
  - Segmentação por contornos: supersegmentação e inserções/substituições em palavras com símbolos compostos.
  - Segmentação por agrupamento: melhoria perceptível; sequência reconhecida mais próxima do esperado, com confianças altas por símbolo.
- Próximos passos:
  - Refinar heurísticas de agrupamento (`max_gap`, área mínima, fusão vertical).
  - Pós-processamento por linguagem/lexicon específico do ELiS.
  - Aumento de dados para símbolos raros e mais variação de deformações.

### Requisitos

- Python 3.10+ (execuções registradas também em 3.11).
- TensorFlow, Pillow, OpenCV, fontTools, imgaug, matplotlib, tqdm, NumPy.
- Ver [requirements.txt](requirements.txt) e [requirements-dev.txt](requirements-dev.txt).

### Como executar no VS Code

1. Abra os notebooks na pasta [notebooks/](notebooks/).
2. Siga a ordem:
   - [notebooks/font_analysis.ipynb](notebooks/font_analysis.ipynb)
   - [notebooks/gererate_dataset.ipynb](notebooks/gererate_dataset.ipynb)
   - [notebooks/train_model.ipynb](notebooks/train_model.ipynb)
   - [notebooks/prediction.ipynb](notebooks/prediction.ipynb)
   - [notebooks/generate_ocr_image_test.ipynb](notebooks/generate_ocr_image_test.ipynb)
   - [notebooks/ocr_groupment.ipynb](notebooks/ocr_groupment.ipynb) e/ou [notebooks/ocr_contourns.ipynb](notebooks/ocr_contourns.ipynb)
3. Use a GPU se disponível (kernels “tf-gpu” demonstrados nos notebooks).

### Apresentação em Slides

[Apresentação em slides do Projeto OCR ELiS](https://github.com/maxwellamaral/OCR_ELiS/blob/main/Projeto%20Final%20-%20DL.pdf)

### Vídeo explicativo do projeto

**Explicação geral**

[![Projeto OCR ELiS](https://i9.ytimg.com/vi_webp/6qfnwk7OBco/mq2.webp?sqp=CPDduMgG-oaymwEmCMACELQB8quKqQMa8AEB-AH-CYAC0AWKAgwIABABGDMgRih_MA8=&rs=AOn4CLDTIygbwrRIELSt-Ub-_VcQ9WpmmA)](https://youtu.be/6qfnwk7OBco?si=tIwltl4KQy_0dHsn)

**Explicação detalhada**

[![Projeto OCR ELiS](https://i9.ytimg.com/vi_webp/6qfnwk7OBco/mq3.webp?sqp=CPDduMgG-oaymwEmCMACELQB8quKqQMa8AEB-AH-CYAC0AWKAgwIABABGE0gWShlMA8=&rs=AOn4CLAV89-xJgWGuPe_hAVdSo-RSkZ1Og)](https://youtu.be/Thz6nTytnro?si=iW7FI4hD2wWRp7jo)

### Referências sobre o ELiS

- BARROS, Mariângela Estelita. Princípios básicos da ELiS. Revista Sinalizar, v. 1, n. 2, p. 204-210, 2016.
- SANTOS, Rayan Soares; VALVERDE, Clodoaldo; BARROS, Mariangela Estelita. QUIMLIBRAS: Objeto virtual de aprendizagem (OVA)  como instrumento de articulação entre a química e a LIBRAS/ELIS. AnápolisUniversidade Federal de Goiás, 2018. Disponível em: <http://www.bdtd.ueg.br/handle/tede/94>. Acesso em: 20 out. 2025
- BARROS, Mariângela Estelita. ELiS – Escrita das Línguas de Sinais: proposta teórica e verificação... phd—[S.l.]: Universidade Federal de Santa Catarina, 2008.

### Citação (BibLaTeX)

Use esta entrada para citar o repositório:

```bibtex
@software{amaralOCRVisografemasELiS2025,
  title = {{{OCR}} de Visografemas {{ELiS}} Com {{CNN}} e Segmentação Por Componentes},
  author = {Amaral, Maxwell Anderson Ielpo and Queiroz, Maria Jane},
  date = {2025},
  location = {João Pessoa},
  url = {https://github.com/maxwellamaral/OCR_ELiS},
  version = {1.0},
  keywords     = {OCR, visão computacional, aprendizado de máquina, redes neurais convolucionais, ELiS, visografemas},
  note         = {Notebooks: análise de fonte, geração de dataset, treino de CNN e OCR por contornos/agrupamento},
  langid = {brazilian}  
}
```
