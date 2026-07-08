import {
  Area,
  AreaChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import { Box, Card, CardContent, Typography } from "@mui/material";

export default function ExposureTrendChart({ data }) {
  return (
    <Card sx={{ mb: 3 }}>
      <CardContent>
        <Typography variant="h5" fontWeight={800} gutterBottom>
          Exposure Trend
        </Typography>

        <Typography color="text.secondary" sx={{ mb: 2 }}>
          Seven-day identity exposure trend.
        </Typography>

        <Box sx={{ height: 260 }}>
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={data}>
              <defs>
                <linearGradient id="exposureGradient" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#22D3EE" stopOpacity={0.8} />
                  <stop offset="95%" stopColor="#22D3EE" stopOpacity={0.05} />
                </linearGradient>
              </defs>

              <CartesianGrid strokeDasharray="3 3" stroke="#1F2937" />
              <XAxis dataKey="day" stroke="#9CA3AF" />
              <YAxis stroke="#9CA3AF" domain={[0, 100]} />
              <Tooltip />
              <Area
                type="monotone"
                dataKey="exposure"
                stroke="#22D3EE"
                fill="url(#exposureGradient)"
                strokeWidth={3}
              />
            </AreaChart>
          </ResponsiveContainer>
        </Box>
      </CardContent>
    </Card>
  );
}