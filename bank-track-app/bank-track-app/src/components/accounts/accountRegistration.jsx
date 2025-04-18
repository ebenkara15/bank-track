import { useAuth } from "@clerk/clerk-react";
import { useState } from "react";
import InstitutionSelector from "../institutions/institutions";



const AccountRegistration = () => {
    const { getToken } = useAuth();
    const [institutionCountry, setinstitutionCountry] = useState('');
    const [institutions, setInstitutions] = useState([]);
    const [institutionId, setinstitutionId] = useState('');
    const [agreementId, setAgreementId] = useState('');
    const [accountId, setAccountId] = useState('');
    const [isError, setIsError] = useState(false);


    return (
        <>
            <form>
                <InstitutionSelector />
            </form>
        </>
    );

};

export default AccountRegistration;
