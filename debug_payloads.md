# MB WAY Debug - Payloads Comparison

## ✅ FUNCIONA (Status 200)
```json
{
  "client_id": "modderstore_c18577a3",
  "client_secret": "850304b9-8f36-4b3d-880f-36ed75514cc7",
  "account_email": "modderstore@gmail.com",
  "amount": 9.00,
  "method": "mbway",
  "payer": {
    "name": "Verification User",
    "document": "999999990",
    "phone": "912345678"
  }
}
```

## ❌ FALHA (Status 500)
```json
{
  "client_id": "modderstore_c18577a3",
  "client_secret": "850304b9-8f36-4b3d-880f-36ed75514cc7",
  "account_email": "modderstore@gmail.com",
  "amount": 9.0,
  "method": "mbway",
  "currency": "EUR",
  "payer": {
    "name": "Anderson silva moutra",
    "document": "987674832",
    "phone": "921876382"
  }
}
```

## Diferenças Identificadas:
1. **name**: "Verification User" vs "Anderson silva moutra"
2. **document**: "999999990" vs "987674832"
3. **phone**: "912345678" vs "921876382"
4. **currency**: ausente vs "EUR"

## Testes Realizados:
- ✅ `912345678` + qualquer nome/NIF = FUNCIONA
- ❌ `921876382` + qualquer nome/NIF = FALHA
- ❌ `919999999` + qualquer nome/NIF = FALHA
- ❌ `912345679` (mudou 1 dígito) = FALHA

## Conclusão Provisória:
O número `912345678` parece ser especial/whitelisted no sistema WayMB.
Outros números (mesmo válidos portugueses) são rejeitados.

## Próximos Passos:
1. Contactar suporte WayMB para perguntar sobre números de teste
2. Verificar se há documentação sobre ambiente sandbox
3. Confirmar se a conta precisa de ativação para aceitar números reais
