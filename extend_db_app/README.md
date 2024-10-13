# ML
На данный момент эта чать кода развернута на вм.:
## Запуск нашего решения

```cmd
python -m venv env
source env/bin/activate
pip install ./req.txt
```

## Запуск
```cmd
python app.py
```

## Запросы

### Запрос в модель
```
curl -N -d "{\"url\": \"https://company.rzd.ru/ru/9353/page/105104?id=1291\"}" -H "X-Requested-With: XMLHttpRequest" -H "Content-Type: application/json" "http://176.109.100.141:5000/upload"
```
