import { useAuth, useUser } from "@clerk/clerk-react";
import axios from 'axios';
import { createContext, useContext, useEffect, useState } from 'react';

export const BankDataContext = createContext();

export const useBankDataContext = () => useContext(BankDataContext);

export const BankDataProvider = ({ children }) => {
    const { isSignedIn, user } = useUser();
    const { getToken } = useAuth();
    const [accounts, setAccounts] = useState(null);
    const [transactions, setTransactions] = useState(null);
    const [balances, setBalances] = useState(null);
    const [categories, setCategories] = useState(null);
    const [isLoading, setIsLoading] = useState(true);
    const [isError, setIsError] = useState(false);


    useEffect(() => {
        async function fetchBankData() {
            axios.defaults.headers.common['Authorization'] = `Bearer ${await getToken()}`;

            // Fetch accounts
            await axios.get('http://localhost:8000/accounts/')
                .then((response) => {
                    const data = response.data

                    console.log('💳 Fetched accounts');
                    console.log(data);

                    if (data.length > 0) {
                        setAccounts(data);
                    }
                })
                .catch((error) => {
                    console.log(error);
                    setIsError(true);
                });

            // Fetch transactions
            await axios.get('http://localhost:8000/transactions/', { params: { limit: 300, sort_type: "desc" } })
                .then((response) => {
                    const data = response.data

                    console.log('💸 Fetched transactions');
                    console.log(data);

                    if (data.length > 0) {
                        setTransactions(data);
                    }
                })
                .catch((error) => {
                    console.log(error);
                    setIsError(true);
                });

            // Fetch balances
            await axios.get('http://localhost:8000/balances/')
                .then((response) => {
                    const data = response.data

                    console.log('⛓️ Fetched balances');
                    console.log(data);

                    if (data.length > 0) {
                        setBalances(data);
                    }
                })
                .catch((error) => {
                    console.log(error);
                    setIsError(true);
                });

            // Fetch categories
            await axios.get('http://localhost:8000/categories/')
                .then((response) => {
                    const data = response.data

                    console.log('📊 Fetched categories');
                    console.log(data);

                    if (data.length > 0) {
                        setCategories(data);
                    }
                })
                .catch((error) => {
                    console.log(error);
                    setIsError(true);
                });
        }

        if (isSignedIn && user) {
            fetchBankData();
            setIsLoading(false);
        }

    }, [getToken, isSignedIn, user]);

    return (
        <BankDataContext.Provider value={{ accounts, transactions, balances, categories, isLoading, setAccounts, setTransactions, setBalances }}>
            {children}
        </BankDataContext.Provider>
    );
};
