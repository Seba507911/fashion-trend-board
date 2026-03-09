import { useQuery } from "@tanstack/react-query";
import axios from "axios";

const api = axios.create({ baseURL: "/api" });

export function useBrands() {
  return useQuery({
    queryKey: ["brands"],
    queryFn: () => api.get("/brands").then((r) => r.data),
  });
}

export function useProducts({ brand, category, season } = {}) {
  return useQuery({
    queryKey: ["products", { brand, category, season }],
    queryFn: () =>
      api
        .get("/products", { params: { brand, category, season } })
        .then((r) => r.data),
  });
}

export function useCategories() {
  return useQuery({
    queryKey: ["categories"],
    queryFn: () => api.get("/products/categories").then((r) => r.data),
  });
}
