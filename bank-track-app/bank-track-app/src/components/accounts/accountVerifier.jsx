import { useAuth, useUser } from '@clerk/clerk-react';
import axios from 'axios';
import { useEffect, useState } from 'react';
import { Navigate, useSearchParams } from 'react-router-dom';

const AccountVerifier = () => {
    const { getToken } = useAuth();
    const { isSignedIn, isLoaded } = useUser();
    const [verified, setVerified] = useState(false);
    const [searchParams, setSearchParams] = useSearchParams();
    const [requisitionId, setRequisitionId] = useState('');

    const acceptRequisition = async () => {
        const token = await getToken();

        axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
        axios.post(`http://localhost:8000/accounts/requisition/accept/${requisitionId}`)
            .then((response) => {
                setVerified(true);
            }).catch((error) => {
                console.error(error);
            });
    };
    useEffect(() => {
        setRequisitionId(searchParams.get('ref'));
        if (requisitionId) {
            acceptRequisition()
        }
    }, [requisitionId, searchParams]);

    if (!isLoaded) {
        return <div>Loading...</div>;
    }

    if (!isSignedIn) {
        return <div><Navigate to='/'>Sign in</Navigate> to view accounts</div>;
    }

    if (verified) {
        return <div>Your account has been successfully verified. <Navigate to='/accounts'>Back to accounts.</Navigate></div>;

    } else {
        return <div>Account not verified</div>;
    }
};

export default AccountVerifier;
