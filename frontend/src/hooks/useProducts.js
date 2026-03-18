import { useQuery } from "@tanstack/react-query";
import axios from "axios";

const api = axios.create({ baseURL: "/api" });

export function useBrands() {
  return useQuery({
    queryKey: ["brands"],
    queryFn: () => api.get("/brands").then((r) => r.data),
  });
}

export function useProducts({ brand, category, season, keyword } = {}) {
  // 브랜드 선택 시 해당 브랜드 전체, 미선택 시 200개
  const limit = brand ? 3000 : 200;
  return useQuery({
    queryKey: ["products", { brand, category, season, keyword }],
    queryFn: () =>
      api
        .get("/products", { params: { brand, category, season, keyword, limit } })
        .then((r) => r.data),
  });
}

export function useCategories() {
  return useQuery({
    queryKey: ["categories"],
    queryFn: () => api.get("/products/categories").then((r) => r.data),
  });
}

export function useTrendChips(season = "26SS") {
  return useQuery({
    queryKey: ["trend-chips", season],
    queryFn: () => api.get("/trendflow-check/trend-chips", { params: { season } }).then((r) => r.data),
  });
}
