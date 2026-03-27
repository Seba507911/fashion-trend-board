import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import axios from "axios";

const api = axios.create({ baseURL: "/api" });

export function useExpertKeywords({ season, category, tier, pool } = {}) {
  return useQuery({
    queryKey: ["expert", "keywords", { season, category, tier, pool }],
    queryFn: () =>
      api
        .get("/expert/keywords", { params: { season, category, tier, pool } })
        .then((r) => r.data),
  });
}

export function useExpertKeywordDetail({ keyword, season } = {}) {
  return useQuery({
    queryKey: ["expert", "detail", keyword, season],
    queryFn: () =>
      api
        .get(`/expert/keyword/${encodeURIComponent(keyword)}/detail`, {
          params: { season },
        })
        .then((r) => r.data),
    enabled: !!keyword,
  });
}

export function useExpertReview() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ keyword, evaluation, comment, reviewer, season }) =>
      api
        .post(`/expert/keyword/${encodeURIComponent(keyword)}/review`, {
          evaluation,
          comment,
          reviewer,
          season,
        })
        .then((r) => r.data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["expert"] });
    },
  });
}
