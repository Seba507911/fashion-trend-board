import { useQuery } from "@tanstack/react-query";
import axios from "axios";

const api = axios.create({ baseURL: "/api" });

export function useTrendFlowKeywords({ season, category } = {}) {
  return useQuery({
    queryKey: ["trendflow-check", "keywords", { season, category }],
    queryFn: () =>
      api
        .get("/trendflow-check/keywords", { params: { season, category, limit: 30 } })
        .then((r) => r.data),
  });
}

export function useTrendFlowKeywordDetail({ keyword, season } = {}) {
  return useQuery({
    queryKey: ["trendflow-check", "detail", keyword, season],
    queryFn: () =>
      api
        .get(`/trendflow-check/keyword/${encodeURIComponent(keyword)}/detail`, {
          params: { season },
        })
        .then((r) => r.data),
    enabled: !!keyword,
  });
}
