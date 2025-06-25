import { useEffect, useState } from 'react';

export default function App() {
  const today = new Date().toISOString().split('T')[0]; // format as YYYY-MM-DD
  const [selectedDate, setSelectedDate] = useState(today);
  const [reservations, setReservations] = useState({});

  useEffect(() => {
    console.log(`⏳ Fetching reservations for: ${selectedDate}`); // ← Added log
    fetch(`/api/reservations/${selectedDate}`)
      .then((res) => res.json())
      .then((data) => setReservations(data))
      .catch((err) => console.error('Failed to fetch reservations:', err));
  }, [selectedDate]);

  return (
    <div style={{ padding: '2rem' }}>
      <h1>Reservations for {selectedDate}</h1>

      <div style={{ marginBottom: '1rem' }}>
        <label htmlFor="date-picker">Select Date: </label>
        <input
          id="date-picker"
          type="date"
          value={selectedDate}
          onChange={(e) => setSelectedDate(e.target.value)}
        />
      </div>

      <table border="1" cellPadding="8">
        <thead>
          <tr>
            <th>Key</th>
            <th>Name</th>
          </tr>
        </thead>
        <tbody>
          {Object.entries(reservations).map(([key, name]) => (
            <tr key={key}>
              <td>{key}</td>
              <td>{name}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
