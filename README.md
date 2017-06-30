# epygone

A very naive epigone and consumer of books.

### System-wide requirements

make sure you have below commands available from CLI.

- python `>= 3.2`
- [aha](https://launchpad.net/ubuntu/+source/aha)
- tree

### Setup

```bash
cd src
pip install -r requirements.txt
python -c "import nltk; nltk.download('punkt')"  # Download the NLTK data
```

### DEMO

You can see epygone in action [here](http://tadek.tele.com.pl/litgen)