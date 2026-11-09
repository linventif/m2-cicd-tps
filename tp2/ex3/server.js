const express = require('express');
const fs = require('fs');
const path = require('path');
const { pipeline, Transform } = require('stream');

const BIG_FILE = path.join(__dirname, 'maybe-big-file.txt');

const app = express();

app.get('/', (req, res) => {
  res.send('Hello world — serveur volontairement non optimisé mais fonctionnel');
});

// Lecture et transformation par morceaux : l'event loop n'est jamais bloquée
// et le fichier n'est jamais chargé entièrement en mémoire.
app.get('/big', (req, res) => {
  const file = fs.createReadStream(BIG_FILE, 'utf8');
  const notFound = () => res.send('Fichier introuvable');
  file.once('error', notFound);
  file.once('open', () => {
    file.off('error', notFound);
    res.type('html');
    const newlinesToBr = new Transform({
      decodeStrings: false,
      transform(chunk, _encoding, callback) {
        callback(null, chunk.replace(/\n/g, '<br/>'));
      },
    });
    pipeline(file, newlinesToBr, res, () => {});
  });
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`Serveur démarré sur le port ${PORT}`);
});
