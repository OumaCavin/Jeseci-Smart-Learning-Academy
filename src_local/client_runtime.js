// Client runtime for Jaclang application
// This file serves as the entry point for Vite compilation
// Jaclang will transform the cl {} block into this runtime

import { jacSpawn, jacLogin, jacSignup, jacLogout, jacIsLoggedIn } from '@jac-client/utils';

console.log('🎓 Jeseci Smart Learning Academy - Client Runtime Loaded');

// Export functions for Jaclang to use
window.jacClient = {
  spawn: jacSpawn,
  login: jacLogin,
  signup: jacSignup,
  logout: jacLogout,
  isLoggedIn: jacIsLoggedIn
};

console.log('✅ Jac Client utilities initialized');