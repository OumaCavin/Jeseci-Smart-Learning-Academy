import * as React from "react";

import * as ReactDOM from "react-dom/client";

import { 
  HashRouter as ReactRouterHashRouter, 
  Routes as ReactRouterRoutes, 
  Route as ReactRouterRoute, 
  Link as ReactRouterLink, 
  Navigate as ReactRouterNavigate, 
  useNavigate as reactRouterUseNavigate, 
  useLocation as reactRouterUseLocation, 
  useParams as reactRouterUseParams 
} from "react-router-dom";

// --- The Missing Helper Functions ---

export function __jacJsx(tag, props, children) {
  if (tag === null) { tag = React.Fragment; }
  let childrenArray = [];
  if (children !== null) {
    if (Array.isArray(children)) { childrenArray = children; } 
    else { childrenArray = [children]; }
  }
  let reactChildren = [];
  for (const child of childrenArray) {
    if (child !== null) { reactChildren.push(child); }
  }
  if (reactChildren.length > 0) {
    let args = [tag, props];
    for (const child of reactChildren) { args.push(child); }
    return React.createElement.apply(React, args);
  } else {
    return React.createElement(tag, props);
  }
}

export const Router = ReactRouterHashRouter;
export const Routes = ReactRouterRoutes;
export const Route = ReactRouterRoute;
export const Link = ReactRouterLink;
export const Navigate = ReactRouterNavigate;
export const useNavigate = reactRouterUseNavigate;
export const useLocation = reactRouterUseLocation;
export const useParams = reactRouterUseParams;

export function useRouter() {
  let navigate = reactRouterUseNavigate();
  let location = reactRouterUseLocation();
  let params = reactRouterUseParams();
  return {"navigate": navigate, "location": location, "params": params, "pathname": location.pathname, "search": location.search, "hash": location.hash};
}

export function navigate(path) {
  window.location.hash = "#" + path;
}

export async function __jacSpawn(left, right, fields) {
  let token = __getLocalStorage("jac_token");
  let url = `/walker/${left}`;
  if (right !== "") { url = `/walker/${left}/${right}`; }
  let response = await fetch(url, {"method": "POST", "accept": "application/json", "headers": {"Content-Type": "application/json", "Authorization": token ? `Bearer ${token}` : ""}, "body": JSON.stringify(fields)});
  if (!response.ok) {
    let error_text = await response.json();
    throw new Error(`Walker failed: ${error_text}`);
  }
  return await response.json();
}

export function jacSpawn(left, right, fields) {
  return __jacSpawn(left, right, fields);
}

export async function __jacCallFunction(function_name, args) {
  let token = __getLocalStorage("jac_token");
  let response = await fetch(`/function/${function_name}`, {"method": "POST", "headers": {"Content-Type": "application/json", "Authorization": token ? `Bearer ${token}` : ""}, "body": JSON.stringify({"args": args})});
  if (!response.ok) {
    let error_text = await response.text();
    throw new Error(`Function ${function_name} failed: ${error_text}`);
  }
  let data = JSON.parse(await response.text());
  return data["result"];
}

export function __getLocalStorage(key) {
  let storage = globalThis.localStorage;
  return storage ? storage.getItem(key) : "";
}

export function __setLocalStorage(key, value) {
  let storage = globalThis.localStorage;
  if (storage) { storage.setItem(key, value); }
}

export function __removeLocalStorage(key) {
  let storage = globalThis.localStorage;
  if (storage) { storage.removeItem(key); }
}

export function jacLogout() { __removeLocalStorage("jac_token"); }

export function jacIsLoggedIn() { let token = __getLocalStorage("jac_token"); return token !== null && token !== ""; }

// Export everything as a module to satisfy the import
export default { __jacJsx, __jacSpawn, Router, Routes, Route, Link, useNavigate };