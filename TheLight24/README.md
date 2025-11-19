# TheLight24 v0.0.0.0.5

Simulazione 2D ad alta frequenza, IA neurale locale, assistente vocale con wake word e STT offline, TTS con profili voce, analisi webcam **on-device**, GUI 60fps con **avatar gatto** lip-sync. Tutto in **locale**. Niente upload di audio o video.
Diretto da Carmine Lamberti
---

## 1) Requisiti VM Ubuntu 24.04 + VirtualBox

- **Audio**: Impostazioni VM → Audio → abilita ingresso microfono.
- **Webcam**: VM → USB 3.0 + filtro USB webcam, poi Dispositivi USB → seleziona la webcam.
  - Alternativa: `VBoxManage controlvm "NomeVM" webcam attach 0`

---

## 2) Trasferimento del progetto

### WinSCP (consigliato)
- Protocollo: SCP
- Host: `127.0.0.1`  Porta: `2222`
- Utente: `ubuntu` (o il tuo utente VM)
- Trascina `TheLight24` in `/home/ubuntu/`

### scp (Git Bash)
```bash
scp -P 2222 -r "C:/percorso/TheLight24" ubuntu@127.0.0.1:/home/ubuntu/
sudo apt install dos2unix -y
dos2unix scripts/*.sh risolve no such file directory in questo caso di script
