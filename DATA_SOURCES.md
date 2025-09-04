# London Historical LLM - Data Sources

## 📚 Overview

The London Historical LLM is trained exclusively on texts from **1500-1850** that are either:
1. **Written by London authors** (born, lived, or worked in London)
2. **Set in London** or reference London extensively
3. **Published in London** during the time period

## 🏛️ Primary Data Sources

### 1. Project Gutenberg
- **URL**: https://www.gutenberg.org/
- **Content**: Public domain books and documents
- **Time Period**: 1500-1850
- **Format**: Plain text files
- **Quality**: High (manually digitized)

### 2. Internet Archive
- **URL**: https://archive.org/
- **Content**: Historical documents, newspapers, books
- **Time Period**: 1500-1850
- **Format**: Various (converted to text)
- **Quality**: Variable (some OCR errors)

## 📖 Complete Text List

### Major Authors & Works (1800-1850)

#### Jane Austen (1775-1817)
- Sense and Sensibility (1811)
- Pride and Prejudice (1813)
- Mansfield Park (1814)
- Emma (1815)
- Northanger Abbey (1818)
- Persuasion (1818)

#### Charles Dickens (1812-1870)
- The Pickwick Papers (1836-37)
- Oliver Twist (1837-39)
- Nicholas Nickleby (1838-39)
- The Old Curiosity Shop (1840-41)
- Barnaby Rudge (1841)
- Martin Chuzzlewit (1843-44)
- A Christmas Carol (1843)
- The Chimes (1844)
- The Cricket on the Hearth (1845)
- The Battle of Life (1846)
- The Haunted Man (1848)
- Dombey and Son (1846-48)
- David Copperfield (1850)

#### Walter Scott (1771-1832)
- Waverley (1814)
- The Antiquary (1816)
- Rob Roy (1817)
- Ivanhoe (1819)
- Kenilworth (1821)
- Heart of Midlothian (1818)
- Bride of Lammermoor (1819)

#### Mary Shelley (1797-1851)
- Frankenstein (1818)
- The Last Man (1826)

#### Charlotte Brontë (1816-1855)
- Jane Eyre (1847)
- Shirley (1849)

#### Emily Brontë (1818-1848)
- Wuthering Heights (1847)

#### Elizabeth Gaskell (1810-1865)
- Mary Barton (1848)

#### Edward Bulwer-Lytton (1803-1873)
- Pelham (1828)
- Paul Clifford (1830)
- Eugene Aram (1832)
- The Last Days of Pompeii (1834)
- Night and Morning (1841)
- The Caxtons (1849)
- The Last of the Barons (1843)

#### William M. Thackeray (1811-1863)
- Vanity Fair (1847-48)
- The Luck of Barry Lyndon (1844)
- Pendennis (1848)

#### Thomas Love Peacock (1785-1866)
- Headlong Hall (1816)
- Nightmare Abbey (1818)
- Melincourt (1817)
- Maid Marian (1822)
- Crotchet Castle (1831)

### Poetry & Literature

#### William Wordsworth (1770-1850)
- Lyrical Ballads (2nd ed.) (1800)
- The Excursion (1814)
- The Prelude (1850)

#### Lord Byron (1788-1824)
- Childe Harold's Pilgrimage, Cantos I–II (1812)
- Childe Harold's Pilgrimage, Canto III (1816)
- Childe Harold's Pilgrimage, Canto IV (1818)
- The Corsair (1814)
- Lara (1814)
- Siege of Corinth (1816)
- Manfred (1817)
- Don Juan, Canto I (1819)

#### Percy Bysshe Shelley (1792-1822)
- Ozymandias (1818)
- Prometheus Unbound (1820)
- Adonais (1821)
- Hymn to Intellectual Beauty (1817)

#### Samuel Taylor Coleridge (1772-1834)
- The Rime of the Ancient Mariner (1817)
- Poems (collected) (1834)

#### John Keats (1795-1821)
- Endymion (1818)
- Isabella; or, The Pot of Basil (1820)
- La Belle Dame sans Merci (1819)
- The Eve of St. Agnes (1820)
- Poems (collected) (1820)

### Political & Economic Texts

#### Thomas Malthus (1766-1834)
- An Essay on the Principle of Population (2nd ed.) (1803)

#### William Cobbett (1763-1835)
- A Plan for Parliamentary Reform (1810)

#### Jeremy Bentham (1748-1832)
- Church-of-Englandism and its Catechism Examined (1818)

#### James Mill (1773-1836)
- Elements of Political Economy (1821)

#### John Stuart Mill (1806-1873)
- A System of Logic Ratiocinative & Inductive (1843)
- Principles of Political Economy (1848)

#### John Austin (1790-1859)
- The Province of Jurisprudence Determined (1832)

#### Harriet Martineau (1802-1876)
- Illustrations of Political Economy (1832)
- Society in America (1837)
- Retrospect of Western Travel (1838)

#### Charles Babbage (1791-1871)
- The Economy of Machinery & Manufactures (1832)

#### Thomas B. Macaulay (1800-1859)
- Report on the Affairs of British India ("Macaulay's Minute") (1835)
- Minute on Indian Education (1835)

### Legal & Political Philosophy

#### Jean-Jacques Rousseau (1712-1778)
- The Social Contract (Eng. trans.) (1803)

#### Montesquieu (1689-1755)
- Spirit of Laws (Eng. trans.) (1805)

#### Emmer de Vattel (1714-1767)
- Of the Law of Nature & of Nations (Eng. trans.) (1806)

## 📊 Data Statistics

### Total Texts: ~200+ works
### Time Period: 1500-1850 (focused on 1800-1850)
### Total Size: ~500MB+ of text
### Authors: 50+ major authors
### Genres: Novels, poetry, political texts, legal documents, philosophy

## 🔍 Data Quality

### High Quality Sources
- **Project Gutenberg**: Manually digitized, high accuracy
- **Original manuscripts**: Some texts from original sources

### Medium Quality Sources
- **Internet Archive**: OCR digitized, some errors
- **Historical reprints**: May have modern annotations

### Quality Control
- **Text cleaning**: Removes headers, footers, page numbers
- **OCR error handling**: Attempts to clean common OCR mistakes
- **Format standardization**: Converts to consistent text format

## 🚀 How Data is Downloaded

The `data_preparation.py` script:

1. **Reads metadata**: From `metadata_london.csv`
2. **Downloads texts**: From Project Gutenberg URLs
3. **Cleans content**: Removes headers, footers, OCR errors
4. **Validates quality**: Ensures substantial content (>1000 chars)
5. **Creates corpus**: Merges all texts into training corpus
6. **Saves metadata**: Tracks download status and quality scores

## 📁 File Structure After Download

```
london_data/
├── london_corpus_merged.txt          # Complete training corpus
├── data_summary.json                 # Download statistics
└── individual_texts/                 # Individual text files
    ├── Pride_and_Prejudice_1813.txt
    ├── Frankenstein_1818.txt
    ├── Oliver_Twist_1837.txt
    └── ... (200+ files)
```

## ⚠️ Important Notes

### Copyright Status
- All texts are in the **public domain**
- No copyright restrictions
- Free to use for any purpose

### Historical Accuracy
- Texts represent the language and views of their time
- May contain outdated or offensive content
- Used for educational and research purposes

### Data Limitations
- Some texts may not be available online
- OCR quality varies
- Some works may be incomplete

## 🔄 Updating the Dataset

To add new texts:

1. **Add to metadata**: Update `metadata_london.csv`
2. **Re-run download**: `python data_preparation.py`
3. **Retrain tokenizer**: `python train_tokenizer_london.py`
4. **Retrain model**: `python train_london_llm.py`

## 📞 Data Sources Contact

- **Project Gutenberg**: https://www.gutenberg.org/
- **Internet Archive**: https://archive.org/
- **Original Repository**: https://github.com/haykgrigo3/TimeCapsuleLLM

---

**Note**: This dataset is curated specifically for training a historical language model. The texts represent the vocabulary, writing style, and worldview of 1500-1850 London, making it perfect for creating an authentic historical AI.
