import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './App.css'
import './index.css'
import {
  createBrowserRouter,
  RouterProvider,
} from "react-router-dom";
import Signin from './component/Signin';


const router = createBrowserRouter([

  {
    path: '/',
    element: <div>This is the landing page</div>
  },
  {
    path: '/sign-in',
    element: <Signin />
  },
  {
    path: '/dash',
    element: <div>this is the dash</div>,
    _children: [
      {
        path: 'main',
        element: <div>this is the main</div>
      }
    ],
    get children() {
      return this._children;
    },
    set children(value) {
      this._children = value;
    },
  },

]);

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <RouterProvider router={router} />
  </StrictMode>
)
