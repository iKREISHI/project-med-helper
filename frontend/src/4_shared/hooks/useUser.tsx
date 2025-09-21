"use client";
import { getCurrentUser, User } from "@/3_entities/user";
import { createContext, useContext, useEffect, useState } from "react";

type UserContextType = {
  user: User | null;
  setUser: React.Dispatch<React.SetStateAction<User | null>>;
  loading: boolean;
  refetchUser: () => void;
};

const UserContext = createContext<UserContextType | undefined>(undefined);

export const UserProvider: React.FC<{ children: React.ReactNode }> = ({
  children,
}) => {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const [refetchTrigger, setRefetchTrigger] = useState(true);

  const refetchUser = () => {
    setRefetchTrigger(prev => !prev);
  };

  useEffect(() => {
    let cancelled = false;

    const fetchUser = async () => {
      try {
        setLoading(true);
        const userData = await getCurrentUser();
        if (!cancelled) {
          setUser(userData);
          setLoading(false);
        }
      } catch (e) {
        if (!cancelled) {
          console.log((e as Error).message || "User Receipt Error");
          setLoading(false);
        }
      }
    };
    
    fetchUser();

    return () => {
      cancelled = true;
    };
  }, [refetchTrigger]);

  return (
    <UserContext.Provider value={{ user, setUser, loading, refetchUser }}>
      {children}
    </UserContext.Provider>
  );
};

export const useUser = () => {
  const context = useContext(UserContext);
  if (!context) throw new Error("useUser must be used within UserProvider");
  return context;
};