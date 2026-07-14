import http from 'k6/http';
import { check } from 'k6';

export const options = {
  vus: 200,
  duration: '3m',
  discardResponseBodies: true,
};

const params = {
  headers: {
    'Content-Type': 'application/json',
    'Connection': 'keep-alive',
  },
};

export default function () {
  const txId = `K6-TX-${__VU}-${__ITER}-${Math.floor(Math.random() * 100000)}`;

  const payload = `{"transaction_id":"${txId}","user_id":"tester_${__VU}_${__ITER}_${Math.floor(Math.random() * 1000)}","Amount":1500.50,"Time":10.0,"V1":0.1,"V2":0.2,"V3":0.3,"V4":0.4,"V5":0.5,"V6":0.6,"V7":0.7,"V8":0.8,"V9":0.9,"V10":0.1,"V11":0.11,"V12":0.12,"V13":0.13,"V14":0.14,"V15":0.15,"V16":0.16,"V17":0.17,"V18":0.18,"V19":0.19,"V20":0.2,"V21":0.21,"V22":0.22,"V23":0.23,"V24":0.24,"V25":0.25,"V26":0.26,"V27":0.27,"V28":0.28}`;
  const res = http.post('http://localhost:8000/api/v1/transactions', payload, params);

  check(res, {
    'is status 202 (Passed/Blocked)': (r) => r.status === 202,
  });
}
