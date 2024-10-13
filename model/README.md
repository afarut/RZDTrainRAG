# ML
На данный момент эта чать кода развернута на вм. Архитектура как в примере бейзлайна [ссылка](http://176.123.167.46:8080):
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
curl -N -d "{\"message\": \"Кому выдаются санаторно-курортные путёвки на отдых?\"}" -H "X-Requested-With: XMLHttpRequest" -H "Content-Type: application/json" "http://176.109.100.141:5000/stream"
```

### Запрос в модель (кнопка подробнее)
```
curl -N -d "{\"message\": \"Кому выдаются санаторно-курортные путёвки на отдых?\"}" -H "X-Requested-With: XMLHttpRequest" -H "Content-Type: application/json" "http://176.109.100.141:5000/more"
```
