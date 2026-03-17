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
  const limit = brand ? 200 : 500;
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
