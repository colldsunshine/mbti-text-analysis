# MBTI Personal Profile

Веб-приложение для построения MBTI-профиля по развёрнутым ответам пользователя.

## Запуск

1. Скачайте файл весов `mbti_stage2_chunked.bin` из раздела Releases и поместите его в `backend/`.
2. Установите зависимости backend:

   ```bash
   python -m pip install -r requirements.txt
   ```

3. Запустите API из корня проекта:

   ```bash
   uvicorn backend.main:app --reload
   ```

4. В отдельном терминале запустите frontend:

   ```bash
   cd frontend
   npm install
   npm run dev
   ```

По умолчанию frontend обращается к `http://localhost:8000/analyze`. Для другого адреса создайте `frontend/.env.local` с переменной `VITE_API_URL`.

## Проверки

```bash
python -m unittest backend.test_inference_rules
cd frontend && npm run lint && npm run build
```
