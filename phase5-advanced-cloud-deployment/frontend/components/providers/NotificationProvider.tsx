'use client';

import { createContext, useContext, useEffect, useState, ReactNode } from 'react';
import { 
  isPushNotificationSupported, 
  registerServiceWorker, 
  subscribeToPushNotifications, 
  isSubscribedToPushNotifications,
  getNotificationPermission
} from '@/lib/notifications';

interface NotificationContextType {
  isSupported: boolean;
  isSubscribed: boolean;
  permission: NotificationPermission;
  subscribe: () => Promise<void>;
}

const NotificationContext = createContext<NotificationContextType | undefined>(undefined);

export function NotificationProvider({ children }: { children: ReactNode }) {
  const [isSupported, setIsSupported] = useState(false);
  const [isSubscribed, setIsSubscribed] = useState(false);
  const [permission, setPermission] = useState<NotificationPermission>('default');

  useEffect(() => {
    const initNotifications = async () => {
      const supported = isPushNotificationSupported();
      setIsSupported(supported);
      
      if (supported) {
        setPermission(getNotificationPermission());
        const subscribed = await isSubscribedToPushNotifications();
        setIsSubscribed(subscribed);
        
        // Register service worker on mount if supported
        await registerServiceWorker();
      }
    };

    initNotifications();
  }, []);

  const subscribe = async () => {
    if (!isSupported) return;
    
    const subscription = await subscribeToPushNotifications();
    if (subscription) {
      setIsSubscribed(true);
      setPermission('granted');
    }
  };

  return (
    <NotificationContext.Provider value={{ isSupported, isSubscribed, permission, subscribe }}>
      {children}
    </NotificationContext.Provider>
  );
}

export function useNotifications() {
  const context = useContext(NotificationContext);
  if (context === undefined) {
    throw new Error('useNotifications must be used within a NotificationProvider');
  }
  return context;
}
